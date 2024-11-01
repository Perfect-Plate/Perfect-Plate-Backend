import os
from fastapi import FastAPI
from dotenv import load_dotenv
import asyncpg
from app.models.allergies import Allergies

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
allergies = []

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

@app.post("/allergies/")
def create_allergies(allergies: Allergies):
    allergies.append(allergies)
    return allergies

@app.get("/allergies/")
def read_allergiess():
    return allergies

@app.put("/allergies/{allergies_id}")
def update_allergies(allergies_id: int, allergies: Allergies):
    allergies[allergies_id] = allergies
    return allergies

@app.delete("/allergies/{allergies_id}")
def delete_allergies(allergies_id: int):
    allergies.pop(allergies_id)
    return {"message": "Allergies deleted"}

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
