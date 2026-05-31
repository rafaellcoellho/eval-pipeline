import json
from datetime import datetime
from pathlib import Path

from loguru import logger


DATASET_PATH = Path(__file__).parent.parent / "dataset_golden_cases"
RESULTS_PATH = Path(__file__).parent.parent / "resultados_processamentos"
ANALYSES_PATH = Path(__file__).parent.parent / "analises_resultados"


class Scorer:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id

        logger.info(f"Scorer iniciado. session_id={session_id}")
        logger.info(f"Dataset: {DATASET_PATH}")
        logger.info(f"Resultados: {RESULTS_PATH}")
        logger.info(f"Análises: {ANALYSES_PATH}")

    def run(self) -> None:
        case_dirs = [d for d in sorted(RESULTS_PATH.iterdir()) if d.is_dir()]
        logger.info(f"Pastas em resultados_processamentos: {len(case_dirs)}")

        for case_dir in case_dirs:
            result_file = self._find_session_result(case_dir)
            if result_file is None:
                logger.debug(f"[{case_dir.name}] Nenhum resultado para session_id={self.session_id}, pulando.")
                continue

            logger.info(f"[{case_dir.name}] Resultado encontrado: {result_file.name}")

            expected = self._load_expected(case_dir.name)
            if expected is None:
                logger.warning(f"[{case_dir.name}] resultado.json não encontrado em dataset_golden_cases, pulando.")
                continue

            obtained = json.loads(result_file.read_text())
            analysis = self._compare(expected, obtained)

            self._save_analysis(case_dir.name, analysis)

    def _find_session_result(self, case_dir: Path) -> Path | None:
        matches = list(case_dir.glob(f"{self.session_id}_*.json"))

        return matches[0] if matches else None

    def _load_expected(self, case_name: str) -> dict | None:
        expected_path = DATASET_PATH / case_name / "resultado.json"

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
        output_dir = ANALYSES_PATH / case_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        output_path = output_dir / f"{self.session_id}_{timestamp}.json"

        output_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2))
        logger.success(f"[{case_name}] Análise salva em {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python scorer.py <session_id>")
        sys.exit(1)

    Scorer(sys.argv[1]).run()
