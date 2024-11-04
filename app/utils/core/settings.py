import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import List

from dotenv import load_dotenv
from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

# Set up logging
log_format = logging.Formatter("%(asctime)s : %(levelname)s - %(message)s")
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
root_logger.addHandler(stream_handler)
logger = logging.getLogger(__name__)


# Application settings
class Settings(BaseSettings):
    API_V1_STR: str = "/v1"
    MONGODB_URL: str = Field(default_factory=lambda: os.getenv("MONGODB_URL"))
    SERVER_HOST: AnyHttpUrl = "https://localhost"
    SERVER_PORT: int = 8000
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    PROJECT_NAME: str = "perfect-plates"


settings = Settings()