import json
import shutil

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
                        "cases": [],
                    }

                analysis = json.loads(f.read_text())
                sessions_map[session_id]["case_count"] += 1
                sessions_map[session_id]["cases"].append(case_dir.name)
                for field_data in analysis.values():
                    breakdown = field_data.get("breakdown", {})
                    if breakdown.get("ignored"):
                        continue
                    sessions_map[session_id]["total_fields"] += breakdown.get(
                        "total", 1
                    )
                    sessions_map[session_id]["correct_fields"] += breakdown.get(
                        "correct", 1 if field_data.get("status") == "acerto" else 0
                    )

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

            global_config_path = get_settings().path_data_files / "config.json"
            global_config = (
                json.loads(global_config_path.read_text())
                if global_config_path.exists()
                else {}
            )
            list_sort_keys = global_config.get("listSortKeys", {})

            fields = [
                {
                    "campo": key,
                    "valor_esperado": v["valor_esperado"],
                    "valor_obtido": v["valor_obtido"],
                    "status": v["status"],
                    "breakdown": v.get("breakdown", {}),
                    "list_sort_key": list_sort_keys.get(key)
                    if isinstance(v["valor_esperado"], list)
                    else None,
                }
                for key, v in analysis.items()
            ]

            total = sum(
                f["breakdown"].get("total", 1)
                for f in fields
                if not f["breakdown"].get("ignored")
            )
            correct = sum(
                f["breakdown"].get("correct", 1 if f["status"] == "acerto" else 0)
                for f in fields
                if not f["breakdown"].get("ignored")
            )

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
    def delete_session(session_id: str) -> None:
        settings = get_settings()
        analysis_root = settings.path_data_files / "analysis"
        processed_root = settings.path_data_files / "processed"

        for root in (analysis_root, processed_root):
            if not root.exists():
                continue
            for case_dir in root.iterdir():
                if case_dir.is_dir():
                    for f in case_dir.glob(f"{session_id}_*.json"):
                        f.unlink()

        notes_path = analysis_root / f"{session_id}.txt"
        if notes_path.exists():
            notes_path.unlink()

    @staticmethod
    def delete_all_sessions() -> None:
        settings = get_settings()

        for subdir in ("analysis", "processed"):
            path = settings.path_data_files / subdir
            if path.exists():
                shutil.rmtree(path)
                path.mkdir()
