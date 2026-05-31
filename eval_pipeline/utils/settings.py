from functools import lru_cache

from eval_pipeline.settings import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()
