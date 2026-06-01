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


class EvalPipelineRunner:
    def __init__(
        self,
        case_names: list[str] | None = None,
        on_case_done: Callable[[str], None] | None = None,
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
        self.on_case_done = on_case_done

        logger.info(f"Runner iniciado. session_id={self.session_id}")
        logger.info(f"Dataset: {self.dataset_path}")
        logger.info(f"Resultados: {self.results_path}")
        logger.info(f"API: {self.api_base_url}")

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

            ticket = self._enviar_arquivo(pdf_path)
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

    def _enviar_arquivo(self, pdf_path: Path) -> str:
        logger.debug(f"Lendo e codificando {pdf_path.name} em base64.")
        arquivo_base64 = base64.b64encode(pdf_path.read_bytes()).decode()

        url = f"{self.api_base_url}/{self.upload_endpoint}"
        logger.debug(f"POST {url}")

        response = requests.post(url, json={"arquivo_base64": arquivo_base64})
        response.raise_for_status()

        return response.json()["ticket"]

    def _aguardar_resultado(self, ticket: str, case_name: str) -> None:
        url = f"{self.api_base_url}/{self.result_endpoint}"

        while True:
            time.sleep(POLLING_INTERVAL_SECONDS)

            logger.debug(f"[{case_name}] POST {url} ticket={ticket}")
            response = requests.post(url, json={"ticket": ticket})
            response.raise_for_status()
            payload = response.json()

            status = payload["status"]
            logger.info(f"[{case_name}] Status: {status}")

            if status == "Finalizado":
                self._salvar_resultado(ticket, case_name, payload)
                return

    @staticmethod
    def _find_pdf(directory: Path) -> Path | None:
        pdfs = list(directory.glob("*.pdf"))

        return pdfs[0] if pdfs else None

    def _salvar_resultado(self, ticket: str, case_name: str, payload: dict) -> None:
        output_dir = self.results_path / case_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        output_path = output_dir / f"{self.session_id}_{timestamp}.json"

        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        logger.success(f"[{case_name}] Resultado salvo em {output_path}")

        if self.on_case_done:
            self.on_case_done(case_name)
