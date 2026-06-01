import json

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse

from eval_pipeline.utils.settings import get_settings
from eval_pipeline.utils.templating import get_templates


class AnalysisView:
    def __init__(self, request: Request) -> None:
        self.request = request

    def render_list(self) -> HTMLResponse:
        return get_templates().TemplateResponse(
            self.request, "analysis/list.html", {"sessions": self._list_sessions()}
        )

    def render_session(self, session_id: str) -> HTMLResponse:
        data = self._get_session(session_id)
        if data is None:
            raise HTTPException(
                status_code=404, detail=f"Análise não encontrada: {session_id}"
            )
        return get_templates().TemplateResponse(
            self.request, "analysis/session.html", {"session": data}
        )

    def render_compare(self, session_ids: list[str]) -> HTMLResponse:
        return get_templates().TemplateResponse(
            self.request,
            "analysis/compare.html",
            {"comparison": self._compare_sessions(session_ids)},
        )

    @staticmethod
    def _list_sessions() -> list[dict]:
        analysis_root = get_settings().path_data_files / "analysis"
        if not analysis_root.exists():
            return []

        sessions_map: dict[str, dict] = {}

        for case_dir in sorted(analysis_root.iterdir()):
            if not case_dir.is_dir():
                continue

            for f in sorted(case_dir.glob("*.json")):
                parts = f.stem.split("_", 1)
                session_id = parts[0]
                timestamp = parts[1] if len(parts) > 1 else ""

                if session_id not in sessions_map:
                    sessions_map[session_id] = {
                        "session_id": session_id,
                        "timestamp": timestamp,
                        "case_count": 0,
                        "total_fields": 0,
                        "correct_fields": 0,
                    }

                analysis = json.loads(f.read_text())
                sessions_map[session_id]["case_count"] += 1
                for field_data in analysis.values():
                    sessions_map[session_id]["total_fields"] += 1
                    if field_data["status"] == "acerto":
                        sessions_map[session_id]["correct_fields"] += 1

        result = sorted(
            sessions_map.values(), key=lambda s: s["timestamp"], reverse=True
        )

        for s in result:
            total = s["total_fields"]
            s["accuracy_pct"] = (
                round(s["correct_fields"] / total * 100) if total > 0 else 0
            )
            notes_path = analysis_root / f"{s['session_id']}.txt"
            s["notes"] = (
                notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""
            )

        return result

    @staticmethod
    def _get_session(session_id: str) -> dict | None:
        analysis_root = get_settings().path_data_files / "analysis"
        if not analysis_root.exists():
            return None

        cases = []

        for case_dir in sorted(analysis_root.iterdir()):
            if not case_dir.is_dir():
                continue

            matches = list(case_dir.glob(f"{session_id}_*.json"))
            if not matches:
                continue

            f = matches[0]
            analysis = json.loads(f.read_text())

            golden_root = get_settings().path_data_files / "golden_cases"
            config_path = golden_root / case_dir.name / "config.json"
            list_sort_keys: dict[str, str | None] = {}
            if config_path.exists():
                list_sort_keys = json.loads(config_path.read_text()).get(
                    "listSortKeys", {}
                )

            fields = [
                {
                    "campo": key,
                    "valor_esperado": v["valor_esperado"],
                    "valor_obtido": v["valor_obtido"],
                    "status": v["status"],
                    "list_sort_key": list_sort_keys.get(key)
                    if isinstance(v["valor_esperado"], list)
                    else None,
                }
                for key, v in analysis.items()
            ]

            total = len(fields)
            correct = sum(1 for field in fields if field["status"] == "acerto")

            cases.append(
                {
                    "name": case_dir.name,
                    "fields_json": json.dumps(fields, ensure_ascii=False),
                    "total": total,
                    "correct": correct,
                    "accuracy_pct": round(correct / total * 100) if total > 0 else 0,
                }
            )

        if not cases:
            return None

        total_fields = sum(c["total"] for c in cases)
        correct_fields = sum(c["correct"] for c in cases)

        first_file = next(
            (
                f
                for case_dir in analysis_root.iterdir()
                if case_dir.is_dir()
                for f in case_dir.glob(f"{session_id}_*.json")
            ),
            None,
        )
        timestamp = first_file.stem.split("_", 1)[1] if first_file else ""

        notes_path = analysis_root / f"{session_id}.txt"
        notes = notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""

        return {
            "session_id": session_id,
            "timestamp": timestamp,
            "cases": cases,
            "notes": notes,
            "total_fields": total_fields,
            "correct_fields": correct_fields,
            "accuracy_pct": round(correct_fields / total_fields * 100)
            if total_fields > 0
            else 0,
        }

    @staticmethod
    def _compare_sessions(session_ids: list[str]) -> dict:
        analysis_root = get_settings().path_data_files / "analysis"

        sessions_data: dict[str, dict] = {sid: {} for sid in session_ids}

        for case_dir in sorted(analysis_root.iterdir()):
            if not case_dir.is_dir():
                continue
            for session_id in session_ids:
                matches = list(case_dir.glob(f"{session_id}_*.json"))
                if matches:
                    sessions_data[session_id][case_dir.name] = json.loads(
                        matches[0].read_text()
                    )

        all_cases = sorted({case for sd in sessions_data.values() for case in sd})

        rows = []
        for case_name in all_cases:
            all_campos = sorted(
                {
                    campo
                    for sid in session_ids
                    for campo in sessions_data[sid].get(case_name, {})
                }
            )
            for campo in all_campos:
                results = {}
                valor_esperado = ""
                for session_id in session_ids:
                    field_data = sessions_data[session_id].get(case_name, {}).get(campo)
                    if field_data:
                        valor_esperado = field_data["valor_esperado"]
                        results[session_id] = {
                            "valor_obtido": field_data["valor_obtido"],
                            "status": field_data["status"],
                        }
                    else:
                        results[session_id] = {
                            "valor_obtido": None,
                            "status": "missing",
                        }

                rows.append(
                    {
                        "case_name": case_name,
                        "campo": campo,
                        "valor_esperado": valor_esperado,
                        "results": results,
                    }
                )

        sessions_summary = []
        for session_id in session_ids:
            total = sum(len(cd) for cd in sessions_data[session_id].values())
            correct = sum(
                1
                for cd in sessions_data[session_id].values()
                for v in cd.values()
                if v["status"] == "acerto"
            )
            sessions_summary.append(
                {
                    "session_id": session_id,
                    "accuracy_pct": round(correct / total * 100) if total > 0 else 0,
                    "correct": correct,
                    "total": total,
                }
            )

        return {"sessions": sessions_summary, "session_ids": session_ids, "rows": rows}
