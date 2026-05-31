from fastapi import Request
from fastapi.responses import HTMLResponse

from eval_pipeline.utils.templating import get_templates


class IndexView:
    def __init__(self, request: Request) -> None:
        self.request = request

    def render(self) -> HTMLResponse:
        return get_templates().TemplateResponse(self.request, "index.html")
