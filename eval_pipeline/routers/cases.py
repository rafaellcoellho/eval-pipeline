from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from eval_pipeline.utils.settings import get_settings


router = APIRouter(prefix="/cases")


@router.get("/{case_name}/pdf")
def serve_pdf(case_name: str) -> FileResponse:
    case_dir = get_settings().path_data_files / "golden_cases" / case_name
    pdfs = list(case_dir.glob("*.pdf"))

    if not pdfs:
        raise HTTPException(status_code=404, detail=f"PDF não encontrado para o caso: {case_name}")

    return FileResponse(pdfs[0], media_type="application/pdf")
