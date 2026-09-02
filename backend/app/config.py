from __future__ import annotations
import os
import secrets
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
SECRET_FILE = DATA_DIR / "database" / "server.secret"

def _persistent_secret() -> str:
    env = os.getenv("JWT_SECRET")
    if env:
        return env
    SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
    if SECRET_FILE.exists():
        return SECRET_FILE.read_text(encoding="utf-8").strip()
    value = secrets.token_urlsafe(48)
    SECRET_FILE.write_text(value, encoding="utf-8")
    return value

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "QA Matrix AI"
    app_env: str = "development"
    api_prefix: str = "/api"
    host: str = "127.0.0.1"
    port: int = 8000
    database_url: str = f"sqlite:///{(DATA_DIR / 'database' / 'qa_matrix.db').as_posix()}"
    jwt_secret: str = _persistent_secret()
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 480
    admin_email: str = "infojr.83@gmail.com"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:4b-instruct"
    ollama_embed_model: str = "embeddinggemma"
    matrix_dir: Path = DATA_DIR / "matrix"
    index_dir: Path = DATA_DIR / "indexes"
    max_upload_mb: int = 20
    request_timeout_seconds: int = 120
    cors_origins: str = "http://localhost:5173"
    public_health_details: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
