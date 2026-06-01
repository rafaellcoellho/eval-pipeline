from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from eval_pipeline.views.analysis import AnalysisView

router = APIRouter()


@router.get("/analysis", response_class=HTMLResponse)
def analysis_list(request: Request) -> HTMLResponse:
    return AnalysisView(request).render_list()


@router.get("/analysis/compare", response_class=HTMLResponse)
def analysis_compare(
    request: Request,
    sessions: list[str] = Query(...),
) -> HTMLResponse:
    return AnalysisView(request).render_compare(sessions)


@router.get("/analysis/{session_id}", response_class=HTMLResponse)
def analysis_session(request: Request, session_id: str) -> HTMLResponse:
    return AnalysisView(request).render_session(session_id)
