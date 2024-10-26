import os
from fastapi import FastAPI
from dotenv import load_dotenv
import asyncpg
from app.models.dietarypreferences import DietaryPreferences

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
preferences = []

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

@app.post("/preferences/")
def create_preference(preference: DietaryPreferences):
    preferences.append(preference)
    return preference

@app.get("/preferences/")
def read_preferences():
    return preferences

@app.put("/preferences/{preference_id}")
def update_preference(preference_id: int, preference: DietaryPreferences):
    preferences[preference_id] = preference
    return preference

@app.delete("/preferences/{preference_id}")
def delete_preference(preference_id: int):
    preferences.pop(preference_id)
    return {"message": "Preference deleted"}

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
