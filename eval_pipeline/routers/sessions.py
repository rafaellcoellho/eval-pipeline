from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from eval_pipeline.views.session_detail import SessionDetailView
from eval_pipeline.views.sessions import SessionsView

router = APIRouter()


@router.get("/sessions", response_class=HTMLResponse)
def sessions_page(request: Request) -> HTMLResponse:
    return SessionsView(request).render()


@router.get("/sessions/{session_id}", response_class=HTMLResponse)
def session_detail_page(request: Request, session_id: str) -> HTMLResponse:
    return SessionDetailView(request, session_id).render()
