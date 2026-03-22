"""Application configuration management."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class AppConfig:
    """Typed runtime configuration loaded from environment variables."""

    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Canberbyte DocFlow AI"))
    app_tagline: str = field(
        default_factory=lambda: os.getenv(
            "APP_TAGLINE",
            "AI-ready PDF to Workflow Conversion Platform",
        )
    )
    company_name: str = field(
        default_factory=lambda: os.getenv("COMPANY_NAME", "Canberbyte Technologies")
    )
    environment: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: Path = field(
        default_factory=lambda: BASE_DIR / os.getenv("LOG_FILE", "logs/app.log")
    )
    output_dir: Path = field(
        default_factory=lambda: BASE_DIR / os.getenv("OUTPUT_DIR", "outputs")
    )
    max_upload_mb: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_MB", "25")))
    auth_users: str = field(
        default_factory=lambda: os.getenv(
            "AUTH_USERS",
            "admin|Admin@123|Admin,user|User@123|User",
        )
    )
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "stub"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-5.4-mini"))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    enable_dark_mode_toggle: bool = field(
        default_factory=lambda: _as_bool(os.getenv("ENABLE_DARK_MODE_TOGGLE", "true"), default=True)
    )

    def ensure_directories(self) -> None:
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


_CONFIG: AppConfig | None = None


def get_config() -> AppConfig:
    """Return a singleton app configuration."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = AppConfig()
        _CONFIG.ensure_directories()
    return _CONFIG
