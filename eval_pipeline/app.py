from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from eval_pipeline.routers import analysis, golden_cases, index, run

STATIC_PATH = Path(__file__).parent.parent / "static"

app = FastAPI(title="eval pipeline")

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.include_router(index.router)
app.include_router(golden_cases.router)

app.include_router(run.router)
app.include_router(analysis.router)
