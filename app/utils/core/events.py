"""
life span events
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.db_connect import client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle events"""
    client.table("users").select("*").execute()
    yield  # You can add any startup logic here if needed
    logging.info("lifespan shutdown")
