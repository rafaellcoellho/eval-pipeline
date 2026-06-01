import json
from collections import Counter
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

            global_config = self._load_global_config()
            list_sort_keys = global_config.get("listSortKeys", {})
            ignore_fields = set(global_config.get("ignoreFields", []))
            obtained = json.loads(result_file.read_text())
            analysis = self._compare(expected, obtained, list_sort_keys, ignore_fields)

            self._save_analysis(case_dir.name, analysis)

    def _find_session_result(self, case_dir: Path) -> Path | None:
        matches = list(case_dir.glob(f"{self.session_id}_*.json"))

        return matches[0] if matches else None

    def _load_expected(self, case_name: str) -> dict | None:
        expected_path = self.dataset_path / case_name / "resultado.json"

        if not expected_path.exists():
            return None

        return json.loads(expected_path.read_text())

    def _load_global_config(self) -> dict:
        config_path = self.dataset_path.parent / "config.json"

        if not config_path.exists():
            return {}

        return json.loads(config_path.read_text())

    def _compare(
        self,
        expected: dict,
        obtained: dict,
        list_sort_keys: dict[str, str | None],
        ignore_fields: set[str],
    ) -> dict:
        analysis = {}

        for key, valor_esperado in expected.items():
            valor_obtido = obtained.get(key)

            if key in ignore_fields:
                breakdown = {"total": 0, "correct": 0, "ignored": True}
                status = "ignorado"
            elif isinstance(valor_esperado, list) and key in list_sort_keys:
                breakdown = self._breakdown_list(
                    valor_esperado, valor_obtido, list_sort_keys[key]
                )
                status = (
                    "acerto" if breakdown["correct"] == breakdown["total"] else "erro"
                )
            elif isinstance(valor_esperado, dict):
                breakdown = self._breakdown_object(valor_esperado, valor_obtido)
                status = (
                    "acerto" if breakdown["correct"] == breakdown["total"] else "erro"
                )
            else:
                match = valor_obtido == valor_esperado
                breakdown = {"total": 1, "correct": 1 if match else 0}
                status = "acerto" if match else "erro"

            analysis[key] = {
                "valor_esperado": valor_esperado,
                "valor_obtido": valor_obtido,
                "status": status,
                "breakdown": breakdown,
            }

            logger.debug(
                f"  {key}: {breakdown['correct']}/{breakdown['total']} -> {status}"
            )

        return analysis

    @staticmethod
    def _breakdown_object(expected: dict, obtained: object) -> dict:
        if not isinstance(obtained, dict):
            return {"total": len(expected), "correct": 0}

        all_keys = list({*expected.keys(), *obtained.keys()})
        correct = sum(1 for k in all_keys if expected.get(k) == obtained.get(k))

        return {"total": len(all_keys), "correct": correct}

    @staticmethod
    def _breakdown_list(expected: list, obtained: object, sort_key: str | None) -> dict:
        if not isinstance(obtained, list):
            total = (
                sum(len(i) for i in expected)
                if (expected and isinstance(expected[0], dict))
                else len(expected)
            )
            return {"total": total, "correct": 0}

        is_object_list = bool(expected) and isinstance(expected[0], dict)

        if is_object_list and sort_key:
            exp_map = {str(item.get(sort_key, "")): item for item in expected}
            obt_map = {str(item.get(sort_key, "")): item for item in obtained}
            all_keys = sorted({*exp_map.keys(), *obt_map.keys()})

            total = 0
            correct = 0

            for k in all_keys:
                exp_item = exp_map.get(k)
                obt_item = obt_map.get(k)

                if exp_item is None:
                    total += len(obt_item)
                elif obt_item is None:
                    total += len(exp_item)
                else:
                    item_keys = list({*exp_item.keys(), *obt_item.keys()})
                    total += len(item_keys)
                    correct += sum(
                        1 for fk in item_keys if exp_item.get(fk) == obt_item.get(fk)
                    )

            return {"total": total, "correct": correct}

        def _serialize(v: object) -> str:
            return json.dumps(v, sort_keys=True) if isinstance(v, dict) else str(v)

        exp_counts = Counter(_serialize(x) for x in expected)
        obt_counts = Counter(_serialize(x) for x in obtained)
        all_items = {*exp_counts.keys(), *obt_counts.keys()}

        correct = sum(min(exp_counts[k], obt_counts.get(k, 0)) for k in exp_counts)
        total = sum(max(exp_counts.get(k, 0), obt_counts.get(k, 0)) for k in all_items)

        return {"total": total, "correct": correct}

    def _save_analysis(self, case_name: str, analysis: dict) -> None:
        output_dir = self.analyses_path / case_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        output_path = output_dir / f"{self.session_id}_{timestamp}.json"

        output_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2))
        logger.success(f"[{case_name}] Análise salva em {output_path}")
