import base64
import hashlib
import math
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from eval_pipeline.settings import Settings

app = FastAPI()

PROCESSING_DELAY_SECONDS = 5

_tickets: dict[str, dict] = {}

_LOREM_BASE = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
    "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
    "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
    "mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit "
    "voluptatem accusantium doloremque laudantium, totam rem aperiam eaque ipsa quae ab illo "
    "inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim "
    "ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur "
    "magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui "
    "dolorem ipsum quia dolor sit amet consectetur adipisci velit, sed quia non numquam eius "
    "modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. "
)
_TEXTO_MUITO_GRANDE = (_LOREM_BASE * math.ceil(10000 / len(_LOREM_BASE)))[:10000]

_LISTA_MUITOS_ITENS: list[dict] = [
    {
        "nomeCompleto": "Ana Paula Ferreira Santos",
        "numeroCpf": "123.456.789-00",
        "enderecoRua": "Rua das Acácias",
        "enderecoNumero": "142",
        "enderecoBairro": "Jardim Primavera",
        "enderecoCidade": "São Paulo",
        "enderecoEstado": "SP",
        "enderecoCep": "01310-100",
        "telefoneResidencial": "(11) 3344-5566",
        "telefoneCelular": "(11) 91234-5678",
        "emailPessoal": "anapaula@email.com",
        "emailProfissional": "ana.santos@empresa.com.br",
        "dataNascimento": "15/03/1990",
        "naturalidade": "São Paulo",
        "nacionalidade": "Brasileira",
        "estadoCivil": "Solteira",
        "grauInstrucao": "Superior Completo",
        "nomeMae": "Maria Aparecida Ferreira",
        "nomePai": "José Carlos Santos",
        "numeroRg": "12.345.678-9",
    },
    {
        "nomeCompleto": "Bruno Henrique Costa Lima",
        "numeroCpf": "234.567.890-11",
        "enderecoRua": "Avenida Paulista",
        "enderecoNumero": "2300",
        "enderecoBairro": "Bela Vista",
        "enderecoCidade": "São Paulo",
        "enderecoEstado": "SP",
        "enderecoCep": "01310-200",
        "telefoneResidencial": "(11) 2233-4455",
        "telefoneCelular": "(11) 98765-4321",
        "emailPessoal": "brunolima@email.com",
        "emailProfissional": "b.lima@empresa.com.br",
        "dataNascimento": "22/07/1985",
        "naturalidade": "Campinas",
        "nacionalidade": "Brasileiro",
        "estadoCivil": "Casado",
        "grauInstrucao": "Pós-Graduação",
        "nomeMae": "Sandra Costa Lima",
        "nomePai": "Roberto Lima Costa",
        "numeroRg": "23.456.789-0",
    },
    {
        "nomeCompleto": "Carla Mendes Oliveira",
        "numeroCpf": "345.678.901-22",
        "enderecoRua": "Rua XV de Novembro",
        "enderecoNumero": "88",
        "enderecoBairro": "Centro",
        "enderecoCidade": "Curitiba",
        "enderecoEstado": "PR",
        "enderecoCep": "80020-310",
        "telefoneResidencial": "(41) 3322-1100",
        "telefoneCelular": "(41) 99988-7766",
        "emailPessoal": "carlamendes@email.com",
        "emailProfissional": "c.oliveira@empresa.com.br",
        "dataNascimento": "09/11/1993",
        "naturalidade": "Curitiba",
        "nacionalidade": "Brasileira",
        "estadoCivil": "Divorciada",
        "grauInstrucao": "Superior Completo",
        "nomeMae": "Lucia Mendes",
        "nomePai": "Antonio Oliveira",
        "numeroRg": "34.567.890-1",
    },
    {
        "nomeCompleto": "Diego Rocha Nascimento",
        "numeroCpf": "456.789.012-33",
        "enderecoRua": "Rua da Bahia",
        "enderecoNumero": "500",
        "enderecoBairro": "Funcionários",
        "enderecoCidade": "Belo Horizonte",
        "enderecoEstado": "MG",
        "enderecoCep": "30160-011",
        "telefoneResidencial": "(31) 3211-4400",
        "telefoneCelular": "(31) 97654-3210",
        "emailPessoal": "diegorocha@email.com",
        "emailProfissional": "d.nascimento@empresa.com.br",
        "dataNascimento": "30/05/1988",
        "naturalidade": "Belo Horizonte",
        "nacionalidade": "Brasileiro",
        "estadoCivil": "Solteiro",
        "grauInstrucao": "Ensino Médio Completo",
        "nomeMae": "Fernanda Rocha",
        "nomePai": "Paulo Nascimento",
        "numeroRg": "45.678.901-2",
    },
    {
        "nomeCompleto": "Elisa Tavares Pinto",
        "numeroCpf": "567.890.123-44",
        "enderecoRua": "Rua Floriano Peixoto",
        "enderecoNumero": "77",
        "enderecoBairro": "Moinhos de Vento",
        "enderecoCidade": "Porto Alegre",
        "enderecoEstado": "RS",
        "enderecoCep": "90035-170",
        "telefoneResidencial": "(51) 3344-2200",
        "telefoneCelular": "(51) 96543-2109",
        "emailPessoal": "elisatavares@email.com",
        "emailProfissional": "e.pinto@empresa.com.br",
        "dataNascimento": "14/01/1996",
        "naturalidade": "Porto Alegre",
        "nacionalidade": "Brasileira",
        "estadoCivil": "Casada",
        "grauInstrucao": "Superior Incompleto",
        "nomeMae": "Beatriz Tavares",
        "nomePai": "Marcelo Pinto",
        "numeroRg": "56.789.012-3",
    },
    {
        "nomeCompleto": "Felipe Gomes Cardoso",
        "numeroCpf": "678.901.234-55",
        "enderecoRua": "Rua do Comércio",
        "enderecoNumero": "321",
        "enderecoBairro": "Comércio",
        "enderecoCidade": "Salvador",
        "enderecoEstado": "BA",
        "enderecoCep": "40015-100",
        "telefoneResidencial": "(71) 3322-5544",
        "telefoneCelular": "(71) 95432-1098",
        "emailPessoal": "felipegomes@email.com",
        "emailProfissional": "f.cardoso@empresa.com.br",
        "dataNascimento": "27/08/1991",
        "naturalidade": "Salvador",
        "nacionalidade": "Brasileiro",
        "estadoCivil": "Solteiro",
        "grauInstrucao": "Técnico Completo",
        "nomeMae": "Renata Gomes",
        "nomePai": "Eduardo Cardoso",
        "numeroRg": "67.890.123-4",
    },
    {
        "nomeCompleto": "Gabriela Souza Ramos",
        "numeroCpf": "789.012.345-66",
        "enderecoRua": "Avenida Boa Viagem",
        "enderecoNumero": "1500",
        "enderecoBairro": "Boa Viagem",
        "enderecoCidade": "Recife",
        "enderecoEstado": "PE",
        "enderecoCep": "51011-000",
        "telefoneResidencial": "(81) 3311-6655",
        "telefoneCelular": "(81) 94321-0987",
        "emailPessoal": "gabrielasouza@email.com",
        "emailProfissional": "g.ramos@empresa.com.br",
        "dataNascimento": "03/12/1987",
        "naturalidade": "Recife",
        "nacionalidade": "Brasileira",
        "estadoCivil": "Viúva",
        "grauInstrucao": "Mestrado",
        "nomeMae": "Claudia Souza",
        "nomePai": "Henrique Ramos",
        "numeroRg": "78.901.234-5",
    },
    {
        "nomeCompleto": "Henrique Alves Monteiro",
        "numeroCpf": "890.123.456-77",
        "enderecoRua": "Rua Sete de Setembro",
        "enderecoNumero": "204",
        "enderecoBairro": "Centro",
        "enderecoCidade": "Fortaleza",
        "enderecoEstado": "CE",
        "enderecoCep": "60050-010",
        "telefoneResidencial": "(85) 3200-7766",
        "telefoneCelular": "(85) 93210-9876",
        "emailPessoal": "henriquealves@email.com",
        "emailProfissional": "h.monteiro@empresa.com.br",
        "dataNascimento": "19/06/1983",
        "naturalidade": "Fortaleza",
        "nacionalidade": "Brasileiro",
        "estadoCivil": "Casado",
        "grauInstrucao": "Doutorado",
        "nomeMae": "Vera Alves",
        "nomePai": "Carlos Monteiro",
        "numeroRg": "89.012.345-6",
    },
]

CASE_RESULTS: dict[str, dict] = {
    "01_exemplo": {
        "textoEstado": "Finalizado",
        "numeroMatricula": "123456789",
        "textoMuitoGrande": _TEXTO_MUITO_GRANDE,
        "produtos": [
            {
                "codigo": "P001",
                "nome": "Notebook Dell",
                "preco": "3500.00",
                "categoria": "Eletronicos",
                "estoque": "15",
                "ativo": "true",
            },
            {
                "codigo": "P002",
                "nome": "Mouse Logitech",
                "preco": "150.00",
                "categoria": "Perifericos",
                "estoque": "42",
                "ativo": "true",
            },
            {
                "codigo": "P003",
                "nome": "Teclado Mecanico",
                "preco": "280.00",
                "categoria": "Perifericos",
                "estoque": "30",
                "ativo": "false",
            },
            {
                "codigo": "P004",
                "nome": "Monitor LG 27pol",
                "preco": "1350.00",
                "categoria": "Monitores",
                "estoque": "8",
                "ativo": "true",
            },
            {
                "codigo": "P006",
                "nome": "Headset Sony",
                "preco": "280.00",
                "categoria": "Audio",
                "estoque": "12",
                "ativo": "true",
            },
        ],
        "listaMuitosItens": _LISTA_MUITOS_ITENS,
        "endereco": {
            "rua": "Rua das Flores",
            "numero": "456",
            "bairro": "Jardim Primavera",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01310-200",
        },
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
