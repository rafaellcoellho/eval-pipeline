from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from eval_pipeline.routers import golden_cases, index, sessions

STATIC_PATH = Path(__file__).parent.parent / "static"

app = FastAPI(title="eval pipeline")

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.include_router(index.router)
app.include_router(golden_cases.router)
app.include_router(sessions.router)
