import base64
import hashlib
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from eval_pipeline.settings import Settings

app = FastAPI()

PROCESSING_DELAY_SECONDS = 5

_tickets: dict[str, dict] = {}

CASE_RESULTS: dict[str, dict] = {
    "01_exemplo": {
        "textoEstado": "Finalizado",
        "numeroMatricula": "123456789",
    },
}


def _build_pdf_hash_map() -> dict[str, str]:
    golden_cases = Settings().path_data_files / "golden_cases"
    mapping: dict[str, str] = {}

    for case_dir in sorted(golden_cases.iterdir()):
        if not case_dir.is_dir():
            continue

        pdfs = list(case_dir.glob("*.pdf"))
        if not pdfs:
            continue

        b64 = base64.b64encode(pdfs[0].read_bytes()).decode()
        ticket = hashlib.sha256(b64.encode()).hexdigest()
        mapping[ticket] = case_dir.name

    return mapping


_PDF_HASH_TO_CASE: dict[str, str] = _build_pdf_hash_map()


class ProcessarArquivoRequest(BaseModel):
    indicadorNovoProcessamento: int
    textoBinarioImagem: str
    quantidadeTamanhoTextoBinarioImagem: int


class ProcessarArquivoResponse(BaseModel):
    codigoBilhete: str


class ConsultarResultadoRequest(BaseModel):
    codigoBilhete: str


@app.post("/processar-arquivo", response_model=ProcessarArquivoResponse)
def processar_arquivo(body: ProcessarArquivoRequest) -> ProcessarArquivoResponse:
    ticket = hashlib.sha256(body.textoBinarioImagem.encode()).hexdigest()
    case_name = _PDF_HASH_TO_CASE.get(ticket, "")
    _tickets[ticket] = {"created_at": time.monotonic(), "case_name": case_name}

    return ProcessarArquivoResponse(codigoBilhete=ticket)


@app.post("/consultar-resultado")
def consultar_resultado(body: ConsultarResultadoRequest) -> dict:
    entry = _tickets.get(body.codigoBilhete)

    if entry is None:
        raise HTTPException(
            status_code=404, detail=f"Ticket não encontrado: {body.codigoBilhete}"
        )

    elapsed = time.monotonic() - entry["created_at"]

    if elapsed < PROCESSING_DELAY_SECONDS:
        return {"textoEstado": "Na fila"}

    case_name = entry["case_name"]

    return CASE_RESULTS.get(
        case_name, {"textoEstado": "Finalizado", "numeroMatricula": "000000000"}
    )
