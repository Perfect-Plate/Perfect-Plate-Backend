"""
life span events
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.database.db_connect import client
from app.utils.core.settings import logger


# Lifespan event manager
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown."""
    # Startup logic
    logger.info("Starting up lifespan event.")
    yield
    # Shutdown logic
    logger.info("Shutting down lifespan event.")
    client.close()

