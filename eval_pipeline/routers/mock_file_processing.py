import hashlib
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

PROCESSING_DELAY_SECONDS = 5

_tickets: dict[str, dict] = {}

CASE_RESULTS: dict[str, dict] = {
    "01_exemplo": {
        "textoEstado": "Finalizado",
        "numeroMatricula": "123456789",
    },
}


class ProcessarArquivoRequest(BaseModel):
    arquivo_base64: str
    case_name: str = ""


class ProcessarArquivoResponse(BaseModel):
    ticket: str


class ConsultarResultadoRequest(BaseModel):
    ticket: str


@app.post("/processar-arquivo", response_model=ProcessarArquivoResponse)
def processar_arquivo(body: ProcessarArquivoRequest) -> ProcessarArquivoResponse:
    ticket = hashlib.sha256(
        f"{body.arquivo_base64}{body.case_name}".encode()
    ).hexdigest()
    _tickets[ticket] = {"created_at": time.monotonic(), "case_name": body.case_name}

    return ProcessarArquivoResponse(ticket=ticket)


@app.post("/consultar-resultado")
def consultar_resultado(body: ConsultarResultadoRequest) -> dict:
    entry = _tickets.get(body.ticket)

    if entry is None:
        raise HTTPException(
            status_code=404, detail=f"Ticket não encontrado: {body.ticket}"
        )

    elapsed = time.monotonic() - entry["created_at"]

    if elapsed < PROCESSING_DELAY_SECONDS:
        return {"textoEstado": "Na fila"}

    case_name = entry["case_name"]

    return CASE_RESULTS.get(
        case_name, {"textoEstado": "Finalizado", "numeroMatricula": "000000000"}
    )
