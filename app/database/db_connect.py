import os
from fastapi import Depends
from dotenv import load_dotenv
import asyncpg

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

# Dependency to access the database connection
async def get_db():
    conn = await connect_to_db()
    try:
        yield conn
    finally:
        await conn.close()



