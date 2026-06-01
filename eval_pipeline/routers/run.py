import shutil
from typing import Annotated

from fastapi import APIRouter, Body, Request
from fastapi.responses import HTMLResponse

from eval_pipeline.services.pipeline import PipelineService
from eval_pipeline.utils.settings import get_settings
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


@router.delete("/run/data")
def clear_all_data() -> dict:
    data_root = get_settings().path_data_files

    for folder in ["analysis", "processed"]:
        path = data_root / folder
        if path.exists():
            shutil.rmtree(path)
            path.mkdir()

    return {"ok": True}
