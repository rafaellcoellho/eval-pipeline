import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from settings import Settings


class Scorer:
    def __init__(self, session_id: str) -> None:
        settings = Settings()

        data_root = settings.path_data_files
        self.dataset_path = data_root / "golden_cases"
        self.results_path = data_root / "processed"
        self.analyses_path = data_root / "analysis"
        self.session_id = session_id

        logger.info(f"Scorer iniciado. session_id={session_id}")
        logger.info(f"Dataset: {self.dataset_path}")
        logger.info(f"Resultados: {self.results_path}")
        logger.info(f"Análises: {self.analyses_path}")

    def run(self) -> None:
        case_dirs = [d for d in sorted(self.results_path.iterdir()) if d.is_dir()]
        logger.info(f"Pastas em processed: {len(case_dirs)}")

        for case_dir in case_dirs:
            result_file = self._find_session_result(case_dir)
            if result_file is None:
                logger.debug(f"[{case_dir.name}] Nenhum resultado para session_id={self.session_id}, pulando.")
                continue

            logger.info(f"[{case_dir.name}] Resultado encontrado: {result_file.name}")

            expected = self._load_expected(case_dir.name)
            if expected is None:
                logger.warning(f"[{case_dir.name}] resultado.json não encontrado em golden_cases, pulando.")
                continue

            obtained = json.loads(result_file.read_text())
            analysis = self._compare(expected, obtained)

            self._save_analysis(case_dir.name, analysis)

    def _find_session_result(self, case_dir: Path) -> Path | None:
        matches = list(case_dir.glob(f"{self.session_id}_*.json"))

        return matches[0] if matches else None

    def _load_expected(self, case_name: str) -> dict | None:
        expected_path = self.dataset_path / case_name / "resultado.json"

        if not expected_path.exists():
            return None

        return json.loads(expected_path.read_text())

    def _compare(self, expected: dict, obtained: dict) -> dict:
        analysis = {}

        for key, valor_esperado in expected.items():
            valor_obtido = obtained.get(key)
            status = "acerto" if valor_obtido == valor_esperado else "erro"

            analysis[key] = {
                "valor_esperado": valor_esperado,
                "valor_obtido": valor_obtido,
                "status": status,
            }

            logger.debug(f"  {key}: esperado={valor_esperado!r} obtido={valor_obtido!r} -> {status}")

        return analysis

    def _save_analysis(self, case_name: str, analysis: dict) -> None:
        output_dir = self.analyses_path / case_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        output_path = output_dir / f"{self.session_id}_{timestamp}.json"

        output_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2))
        logger.success(f"[{case_name}] Análise salva em {output_path}")
