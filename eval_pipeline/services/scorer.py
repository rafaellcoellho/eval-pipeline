import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from eval_pipeline.settings import Settings


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
                logger.debug(
                    f"[{case_dir.name}] Nenhum resultado para session_id={self.session_id}, pulando."
                )
                continue

            logger.info(f"[{case_dir.name}] Resultado encontrado: {result_file.name}")

            expected = self._load_expected(case_dir.name)
            if expected is None:
                logger.warning(
                    f"[{case_dir.name}] resultado.json não encontrado em golden_cases, pulando."
                )
                continue

            list_sort_keys = self._load_list_sort_keys(case_dir.name)
            obtained = json.loads(result_file.read_text())
            analysis = self._compare(expected, obtained, list_sort_keys)

            self._save_analysis(case_dir.name, analysis)

    def _find_session_result(self, case_dir: Path) -> Path | None:
        matches = list(case_dir.glob(f"{self.session_id}_*.json"))

        return matches[0] if matches else None

    def _load_expected(self, case_name: str) -> dict | None:
        expected_path = self.dataset_path / case_name / "resultado.json"

        if not expected_path.exists():
            return None

        return json.loads(expected_path.read_text())

    def _load_list_sort_keys(self, case_name: str) -> dict[str, str | None]:
        config_path = self.dataset_path / case_name / "config.json"

        if not config_path.exists():
            return {}

        return json.loads(config_path.read_text()).get("listSortKeys", {})

    def _compare(
        self, expected: dict, obtained: dict, list_sort_keys: dict[str, str | None]
    ) -> dict:
        analysis = {}

        for key, valor_esperado in expected.items():
            valor_obtido = obtained.get(key)

            if isinstance(valor_esperado, list) and key in list_sort_keys:
                match = self._compare_lists(
                    valor_esperado, valor_obtido, list_sort_keys[key]
                )
            else:
                match = valor_obtido == valor_esperado

            status = "acerto" if match else "erro"
            analysis[key] = {
                "valor_esperado": valor_esperado,
                "valor_obtido": valor_obtido,
                "status": status,
            }

            logger.debug(f"  {key}: {status}")

        return analysis

    @staticmethod
    def _compare_lists(expected: list, obtained: object, sort_key: str | None) -> bool:
        if not isinstance(obtained, list):
            return False

        if len(expected) != len(obtained):
            return False

        if sort_key is None:
            return sorted(str(x) for x in expected) == sorted(str(x) for x in obtained)

        return sorted(
            expected, key=lambda x: x.get(sort_key, "") if isinstance(x, dict) else ""
        ) == sorted(
            obtained, key=lambda x: x.get(sort_key, "") if isinstance(x, dict) else ""
        )

    def _save_analysis(self, case_name: str, analysis: dict) -> None:
        output_dir = self.analyses_path / case_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        output_path = output_dir / f"{self.session_id}_{timestamp}.json"

        output_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2))
        logger.success(f"[{case_name}] Análise salva em {output_path}")
