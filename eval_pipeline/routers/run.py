from typing import Annotated

from fastapi import APIRouter, Body, Request
from fastapi.responses import HTMLResponse

from eval_pipeline.services.pipeline import PipelineService
from eval_pipeline.views.run import RunView

router = APIRouter()


@router.get("/run", response_class=HTMLResponse)
def run_page(request: Request) -> HTMLResponse:
    return RunView(request).render_selection()


@router.post("/run")
def start_run(
    case_names: Annotated[list[str], Body(embed=True)],
) -> dict:
    session_id = PipelineService.start_run(case_names)
    return {"session_id": session_id}


@router.get("/run/{session_id}", response_class=HTMLResponse)
def run_monitoring_page(request: Request, session_id: str) -> HTMLResponse:
    session = PipelineService.get_session(session_id)

    if session is None:
        return RunView(request).render_selection()

    cases = [
        {"name": name, "status": status} for name, status in session["cases"].items()
    ]

    return RunView(request).render_monitoring(session_id, cases)


@router.get("/run/{session_id}/status")
def run_status(session_id: str) -> dict:
    return PipelineService.get_status(session_id)


@router.post("/run/{session_id}/stop")
def stop_session(session_id: str) -> dict:
    PipelineService.stop_session(session_id)
    return {"ok": True}


@router.post("/run/{session_id}/stop-and-analyze")
def stop_and_analyze(session_id: str) -> dict:
    PipelineService.stop_and_analyze(session_id)
    return {"ok": True}
