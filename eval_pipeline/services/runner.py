import base64
import json
import threading
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import requests
from loguru import logger

from eval_pipeline.settings import Settings

POLLING_INTERVAL_SECONDS = 3
TERMINAL_STATUSES = {"Finalizado", "Falhou", "Cancelado"}


class EvalPipelineRunner:
    def __init__(
        self,
        case_names: list[str] | None = None,
        on_case_started: Callable[[str], None] | None = None,
        on_case_status_changed: Callable[[str, str], None] | None = None,
        on_case_done: Callable[[str], None] | None = None,
        on_case_error: Callable[[str], None] | None = None,
    ) -> None:
        settings = Settings()

        data_root = settings.path_data_files
        self.dataset_path = data_root / "golden_cases"
        self.results_path = data_root / "processed"
        self.api_base_url = settings.url_base_servico_processamento.rstrip("/")
        self.upload_endpoint = settings.endpoint_upload
        self.result_endpoint = settings.endpoint_resultado
        self.session_id = uuid.uuid4().hex[:12]
        self.case_names = case_names
        self.on_case_started = on_case_started
        self.on_case_status_changed = on_case_status_changed
        self.on_case_done = on_case_done
        self.on_case_error = on_case_error
        self.stop_event = threading.Event()
        self.run_scorer_after_stop = False

        logger.info(f"Runner iniciado. session_id={self.session_id}")
        logger.info(f"Dataset: {self.dataset_path}")
        logger.info(f"Resultados: {self.results_path}")
        logger.info(f"API: {self.api_base_url}")

    def stop(self, run_scorer_after: bool = False) -> None:
        self.run_scorer_after_stop = run_scorer_after
        self.stop_event.set()

    def run(self) -> None:
        all_dirs = [d for d in sorted(self.dataset_path.iterdir()) if d.is_dir()]

        case_dirs = (
            [d for d in all_dirs if d.name in self.case_names]
            if self.case_names is not None
            else all_dirs
        )

        logger.info(f"Casos a processar: {len(case_dirs)}")
        threads = []

        for case_dir in case_dirs:
            pdf_path = self._find_pdf(case_dir)
            if pdf_path is None:
                logger.warning(f"[{case_dir.name}] Nenhum PDF encontrado, pulando.")
                continue

            logger.info(f"[{case_dir.name}] PDF encontrado: {pdf_path.name}")

            ticket = self._enviar_arquivo(pdf_path, case_dir.name)
            logger.info(f"[{case_dir.name}] Arquivo enviado. Ticket: {ticket}")

            thread = threading.Thread(
                target=self._aguardar_resultado,
                args=(ticket, case_dir.name),
                daemon=True,
            )
            thread.start()
            threads.append(thread)

        logger.info(f"Aguardando {len(threads)} thread(s) finalizarem...")

        for thread in threads:
            thread.join()

        logger.info("Todas as threads finalizadas.")

    def _enviar_arquivo(self, pdf_path: Path, case_name: str) -> str:
        logger.debug(f"Lendo e codificando {pdf_path.name} em base64.")
        arquivo_base64 = base64.b64encode(pdf_path.read_bytes()).decode()

        url = f"{self.api_base_url}/{self.upload_endpoint}"
        logger.debug(f"POST {url}")

        response = requests.post(
            url,
            json={
                "indicadorNovoProcessamento": 1,
                "textoBinarioImagem": arquivo_base64,
                "quantidadeTamanhoTextoBinarioImagem": len(arquivo_base64),
            },
        )
        response.raise_for_status()

        return response.json()["codigoBilhete"]

    def _aguardar_resultado(self, ticket: str, case_name: str) -> None:
        if self.on_case_started:
            self.on_case_started(case_name)

        started_at = time.monotonic()
        url = f"{self.api_base_url}/{self.result_endpoint}"

        while True:
            interrupted = self.stop_event.wait(timeout=POLLING_INTERVAL_SECONDS)
            if interrupted:
                logger.info(f"[{case_name}] Polling interrompido.")
                return

            logger.debug(f"[{case_name}] POST {url} codigoBilhete={ticket}")
            response = requests.post(url, json={"codigoBilhete": ticket})
            response.raise_for_status()
            payload = response.json()

            status = payload["textoEstado"]
            logger.info(f"[{case_name}] textoEstado: {status}")

            if self.on_case_status_changed:
                self.on_case_status_changed(case_name, status)

            if status == "Finalizado":
                duration = time.monotonic() - started_at
                self._salvar_resultado(ticket, case_name, payload, duration)
                if self.on_case_done:
                    self.on_case_done(case_name)
                return

            if status in TERMINAL_STATUSES:
                if self.on_case_error:
                    self.on_case_error(case_name)
                return

    @staticmethod
    def _find_pdf(directory: Path) -> Path | None:
        pdfs = list(directory.glob("*.pdf"))

        return pdfs[0] if pdfs else None

    def _salvar_resultado(
        self,
        ticket: str,
        case_name: str,
        payload: dict,
        duration_seconds: float | None = None,
    ) -> None:
        output_dir = self.results_path / case_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        output_path = output_dir / f"{self.session_id}_{timestamp}.json"

        data = dict(payload)
        if duration_seconds is not None:
            data["__duration_seconds__"] = round(duration_seconds, 1)

        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        logger.success(f"[{case_name}] Resultado salvo em {output_path}")
