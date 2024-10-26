import os

from fastapi import FastAPI, Depends
from dotenv import load_dotenv
import asyncpg

from app.models.dietarypreferences import DietaryPreferences

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

DATABASE_URL = DATABASE_URL = os.getenv("DATABASE_URL")


async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn


# Use lifespan event handler
@app.lifespan()
async def lifespan(app: FastAPI):
    app.state.db = await connect_to_db()
    yield  # This will run the shutdown event
    await app.state.db.close()


# Dependency to access the database connection
async def get_db():
    return app.state.db


# Example route that uses the database connection
@app.get("/users")
async def read_users(db=Depends(get_db)):
    users = await db.fetch("SELECT * FROM users;")
    return users
