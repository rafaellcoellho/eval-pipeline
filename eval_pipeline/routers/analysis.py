from fastapi import APIRouter, Body, Request
from fastapi.responses import HTMLResponse

from eval_pipeline.utils.settings import get_settings
from eval_pipeline.views.analysis import AnalysisView

router = APIRouter()


@router.get("/analysis", response_class=HTMLResponse)
def analysis_list(request: Request) -> HTMLResponse:
    return AnalysisView(request).render_list()


@router.delete("/analysis")
def delete_all_analyses() -> dict:
    AnalysisView.delete_all_sessions()
    return {"ok": True}


@router.get("/analysis/{session_id}", response_class=HTMLResponse)
def analysis_session(request: Request, session_id: str) -> HTMLResponse:
    return AnalysisView(request).render_session(session_id)


@router.delete("/analysis/{session_id}")
def delete_analysis(session_id: str) -> dict:
    AnalysisView.delete_session(session_id)
    return {"ok": True}


@router.put("/analysis/{session_id}/notes")
def save_notes(session_id: str, text: str = Body(..., embed=True)) -> dict:
    notes_path = get_settings().path_data_files / "analysis" / f"{session_id}.txt"
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.write_text(text, encoding="utf-8")
    return {"ok": True}
