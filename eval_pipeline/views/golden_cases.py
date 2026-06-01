import json

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse

from eval_pipeline.utils.settings import get_settings
from eval_pipeline.utils.templating import get_templates


class GoldenCasesView:
    def __init__(self, request: Request) -> None:
        self.request = request

    def render(self) -> HTMLResponse:
        return get_templates().TemplateResponse(
            self.request,
            "golden_cases/golden_cases.html",
            {"cases": self._list_cases()},
        )

    def render_detail(self, case_name: str) -> HTMLResponse:
        case = self._load_case(case_name)
        if case is None:
            raise HTTPException(
                status_code=404, detail=f"Caso não encontrado: {case_name}"
            )

        return get_templates().TemplateResponse(
            self.request,
            "golden_cases/detail.html",
            {"case": case},
        )

    @staticmethod
    def _list_cases() -> list[dict]:
        golden_cases_path = get_settings().path_data_files / "golden_cases"
        cases = []

        for case_dir in sorted(golden_cases_path.iterdir()):
            if not case_dir.is_dir():
                continue

            cases.append({"name": case_dir.name})

        return cases

    @staticmethod
    def _load_case(case_name: str) -> dict | None:
        case_dir = get_settings().path_data_files / "golden_cases" / case_name
        if not case_dir.is_dir():
            return None

        resultado_path = case_dir / "resultado.json"
        resultado = (
            json.loads(resultado_path.read_text()) if resultado_path.exists() else {}
        )

        pdfs = list(case_dir.glob("*.pdf"))

        return {
            "name": case_name,
            "pdf_filename": pdfs[0].name if pdfs else "",
            "has_ocr": (case_dir / "ocr.txt").exists(),
            "resultado_json": json.dumps(resultado, ensure_ascii=False, indent=2),
        }
