import json

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse

from eval_pipeline.utils.settings import get_settings
from eval_pipeline.utils.templating import get_templates


class SessionDetailView:
    def __init__(self, request: Request, session_id: str) -> None:
        self.request = request
        self.session_id = session_id

    def render(self) -> HTMLResponse:
        cases = self._load_cases()

        if not cases:
            raise HTTPException(
                status_code=404, detail=f"Sessão não encontrada: {self.session_id}"
            )

        return get_templates().TemplateResponse(
            self.request,
            "sessions/session_detail.html",
            {"session_id": self.session_id, "cases": cases},
        )

    def _load_cases(self) -> list[dict]:
        settings = get_settings()
        processed_root = settings.path_data_files / "processed"
        golden_cases_root = settings.path_data_files / "golden_cases"
        cases = []

        for case_dir in sorted(processed_root.iterdir()):
            if not case_dir.is_dir():
                continue

            matches = list(case_dir.glob(f"{self.session_id}_*.json"))
            if not matches:
                continue

            actual_file = matches[0]
            actual = json.loads(actual_file.read_text())

            expected_path = golden_cases_root / case_dir.name / "resultado.json"
            expected = (
                json.loads(expected_path.read_text()) if expected_path.exists() else {}
            )

            cases.append(
                {
                    "name": case_dir.name,
                    "filename": actual_file.name,
                    "expected_json": json.dumps(expected, ensure_ascii=False),
                    "actual_json": json.dumps(actual, ensure_ascii=False),
                }
            )

        return cases
