import json

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

from eval_pipeline.utils.settings import get_settings
from eval_pipeline.views.golden_cases import GoldenCasesView

router = APIRouter()


@router.get("/golden-cases", response_class=HTMLResponse)
def golden_cases_page(request: Request) -> HTMLResponse:
    return GoldenCasesView(request).render()


@router.get("/golden-cases/{case_name}", response_class=HTMLResponse)
def golden_case_detail(request: Request, case_name: str) -> HTMLResponse:
    return GoldenCasesView(request).render_detail(case_name)


@router.get("/cases/{case_name}/pdf")
def serve_pdf(case_name: str) -> FileResponse:
    case_dir = get_settings().path_data_files / "golden_cases" / case_name
    pdfs = list(case_dir.glob("*.pdf"))

    if not pdfs:
        raise HTTPException(status_code=404, detail=f"PDF não encontrado: {case_name}")

    return FileResponse(pdfs[0], media_type="application/pdf")


@router.get("/cases/{case_name}/resultado")
def get_resultado(case_name: str) -> dict:
    path = (
        get_settings().path_data_files / "golden_cases" / case_name / "resultado.json"
    )

    if not path.exists():
        raise HTTPException(status_code=404, detail="resultado.json não encontrado")

    return json.loads(path.read_text())


@router.put("/cases/{case_name}/resultado")
def save_resultado(case_name: str, body: dict = Body(...)) -> dict:
    path = (
        get_settings().path_data_files / "golden_cases" / case_name / "resultado.json"
    )

    if not path.parent.exists():
        raise HTTPException(status_code=404, detail=f"Caso não encontrado: {case_name}")

    path.write_text(json.dumps(body, ensure_ascii=False, indent=4))

    return {"ok": True}


@router.get("/cases/{case_name}/ocr")
def get_ocr(case_name: str) -> dict:
    path = get_settings().path_data_files / "golden_cases" / case_name / "ocr.txt"

    if not path.exists():
        raise HTTPException(status_code=404, detail="ocr.txt não encontrado")

    return {"text": path.read_text()}


@router.get("/cases/{case_name}/processed/{filename}")
def get_processed_result(case_name: str, filename: str) -> dict:
    file_path = get_settings().path_data_files / "processed" / case_name / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resultado não encontrado")

    return json.loads(file_path.read_text())
