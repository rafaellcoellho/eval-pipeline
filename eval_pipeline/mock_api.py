import hashlib
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

PROCESSING_DELAY_SECONDS = 5

_tickets: dict[str, float] = {}


class ProcessarArquivoRequest(BaseModel):
    arquivo_base64: str


class ProcessarArquivoResponse(BaseModel):
    ticket: str


class ConsultarResultadoResponse(BaseModel):
    status: str
    numero_matricula: str


def _gerar_ticket(arquivo_base64: str) -> str:
    return hashlib.sha256(arquivo_base64.encode()).hexdigest()


def _derivar_matricula(ticket: str) -> str:
    return str(int(ticket[:8], 16) % 900_000 + 100_000)


@app.post("/processar-arquivo", response_model=ProcessarArquivoResponse)
def processar_arquivo(body: ProcessarArquivoRequest) -> ProcessarArquivoResponse:
    ticket = _gerar_ticket(body.arquivo_base64)
    _tickets[ticket] = time.monotonic()

    return ProcessarArquivoResponse(ticket=ticket)


class ConsultarResultadoRequest(BaseModel):
    ticket: str


@app.post("/consultar-resultado", response_model=ConsultarResultadoResponse)
def consultar_resultado(body: ConsultarResultadoRequest) -> ConsultarResultadoResponse:
    criado_em = _tickets.get(body.ticket)

    if criado_em is None:
        raise HTTPException(status_code=404, detail=f"Ticket não encontrado: {body.ticket}")

    elapsed = time.monotonic() - criado_em

    if elapsed < PROCESSING_DELAY_SECONDS:
        return ConsultarResultadoResponse(status="Na fila", numero_matricula="")

    return ConsultarResultadoResponse(
        status="Finalizado",
        numero_matricula=_derivar_matricula(body.ticket),
    )
