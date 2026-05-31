from functools import lru_cache

from fastapi.templating import Jinja2Templates

from eval_pipeline.utils.settings import get_settings


@lru_cache
def get_templates() -> Jinja2Templates:
    return Jinja2Templates(directory=get_settings().templates_path)
