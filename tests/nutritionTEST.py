import os
from fastapi import FastAPI
from dotenv import load_dotenv
import asyncpg
from app.models.nutrition import Nutrition

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
nutritions = []

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

@app.post("/recipe_details/")
def create_nutrition(nutrition: Nutrition):
    nutritions.append(nutrition)
    return nutritions

@app.get("/recipe_details/")
def read_nutrition():
    return nutritions

@app.put("/recipe_details/{Nutrition_id}")
def update_Nutrition(Nutrition_id: int, Nutrition: Nutrition):
    nutritions[Nutrition_id] = Nutrition
    return Nutrition

@app.delete("/recipe_details/{Nutrition_id}")
def delete_Nutrition(Nutrition_id: int):
    nutritions.pop(Nutrition_id)
    return {"message": "Nutrition deleted"}

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
