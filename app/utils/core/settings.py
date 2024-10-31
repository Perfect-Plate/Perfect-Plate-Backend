import logging
import os
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, ConfigDict, Field
from pydantic_settings import BaseSettings

log_format = logging.Formatter("%(asctime)s : %(levelname)s - %(message)s")

# root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# standard stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)
load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/v1"
    SUPABASE_URL: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL"))
    SUPABASE_KEY: str = Field(default_factory=lambda: os.getenv("SUPABASE_KEY"))
    SERVER_HOST: AnyHttpUrl = "https://localhost"
    SERVER_PORT: int = 8000

    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    PROJECT_NAME: str = "perfect-plates"
    Config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)


settings = Settings()
