import json

from fastapi import Request
from fastapi.responses import HTMLResponse

from eval_pipeline.utils.settings import get_settings
from eval_pipeline.utils.templating import get_templates


class SessionsView:
    def __init__(self, request: Request) -> None:
        self.request = request

    def render(self) -> HTMLResponse:
        return get_templates().TemplateResponse(
            self.request, "sessions/sessions.html", {"sessions": self._list_sessions()}
        )

    @staticmethod
    def _list_sessions() -> list[dict]:
        processed_root = get_settings().path_data_files / "processed"

        if not processed_root.exists():
            return []

        sessions_map: dict[str, dict] = {}

        for case_dir in sorted(processed_root.iterdir()):
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
                        "cases": [],
                    }

                sessions_map[session_id]["cases"].append(
                    {
                        "name": case_dir.name,
                        "filename": f.name,
                    }
                )

        result = sorted(
            sessions_map.values(), key=lambda s: s["timestamp"], reverse=True
        )

        for s in result:
            s["case_count"] = len(s["cases"])
            s["cases_json"] = json.dumps(s["cases"], ensure_ascii=False)

        return result
