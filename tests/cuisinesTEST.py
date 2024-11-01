import os
from fastapi import FastAPI
from dotenv import load_dotenv
import asyncpg
from app.models.cuisines import Cuisines

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
cuisines = []

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

@app.post("/cuisines/")
def create_cuisines(cuisines: Cuisines):
    cuisines.append(cuisines)
    return cuisines

@app.get("/cuisines/")
def read_cuisines():
    return cuisines

@app.put("/cuisines/{cuisines_id}")
def update_cuisines(cuisines_id: int, cuisines: Cuisines):
    cuisines[cuisines_id] = cuisines
    return cuisines

@app.delete("/cuisines/{cuisines_id}")
def delete_cuisines(cuisines_id: int):
    cuisines.pop(cuisines_id)
    return {"message": "Preference deleted"}

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
