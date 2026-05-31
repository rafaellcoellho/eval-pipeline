from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from eval_pipeline.views.index import IndexView

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return IndexView(request).render()
