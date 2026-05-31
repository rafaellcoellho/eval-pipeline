from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
    )

    url_base_servico_processamento: str
    endpoint_upload: str
    endpoint_resultado: str
    path_data_files: Path

    @field_validator("path_data_files", mode="before")
    @classmethod
    def expand_path(cls, v: str) -> Path:
        return Path(v).expanduser()
