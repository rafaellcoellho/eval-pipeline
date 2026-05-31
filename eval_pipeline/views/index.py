import json

from fastapi import Request
from fastapi.responses import HTMLResponse

from eval_pipeline.utils.settings import get_settings
from eval_pipeline.utils.templating import get_templates


class IndexView:
    def __init__(self, request: Request) -> None:
        self.request = request

    def render(self) -> HTMLResponse:
        return get_templates().TemplateResponse(
            self.request, "index.html", {"cases": self._list_cases()}
        )

    @staticmethod
    def _list_cases() -> list[dict]:
        golden_cases_path = get_settings().path_data_files / "golden_cases"
        cases = []

        for case_dir in sorted(golden_cases_path.iterdir()):
            if not case_dir.is_dir():
                continue

            resultado_path = case_dir / "resultado.json"
            resultado = (
                json.loads(resultado_path.read_text())
                if resultado_path.exists()
                else {}
            )

            pdfs = list(case_dir.glob("*.pdf"))
            pdf_filename = pdfs[0].name if pdfs else ""

            cases.append(
                {
                    "name": case_dir.name,
                    "pdf_filename": pdf_filename,
                    "resultado_filename": resultado_path.name
                    if resultado_path.exists()
                    else "resultado.json",
                    "resultado": json.dumps(resultado, ensure_ascii=False),
                }
            )

        return cases
