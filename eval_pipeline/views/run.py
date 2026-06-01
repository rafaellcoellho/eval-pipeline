from fastapi import Request
from fastapi.responses import HTMLResponse

from eval_pipeline.utils.settings import get_settings
from eval_pipeline.utils.templating import get_templates


class RunView:
    def __init__(self, request: Request) -> None:
        self.request = request

    def render_selection(self) -> HTMLResponse:
        return get_templates().TemplateResponse(
            self.request,
            "run/run.html",
            {"mode": "selection", "cases": self._list_case_names()},
        )

    def render_monitoring(self, session_id: str, cases: list[dict]) -> HTMLResponse:
        return get_templates().TemplateResponse(
            self.request,
            "run/run.html",
            {"mode": "monitoring", "session_id": session_id, "cases": cases},
        )

    @staticmethod
    def _list_case_names() -> list[str]:
        golden_cases_path = get_settings().path_data_files / "golden_cases"
        return sorted(d.name for d in golden_cases_path.iterdir() if d.is_dir())
