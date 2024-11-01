import os
from app.models.recipe_details import RecipeDetails
from fastapi import FastAPI
from dotenv import load_dotenv
import asyncpg
from fastapi.testclient import TestClient

app = FastAPI()

client = TestClient(app)
# Load environment variables from .env file
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
recipe_detail = []

# TEST FILE FOR RECIPE_DETAILS DATACLASS CRUD OPERATIONS

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

@app.post("/recipe_details/")
def create_recipe_details(recipe_details: RecipeDetails):
    recipe_detail.append(recipe_details)
    return recipe_detail

@app.get("/recipe_details/")
def read_recipe_details():
    return recipe_detail

@app.put("/recipe_details/{recipe_details_id}")
def update_recipe_details(recipe_details_id: int, recipe_details: RecipeDetails):
    recipe_detail[recipe_details_id] = recipe_details
    return recipe_details

@app.delete("/recipe_details/{recipe_details_id}")
def delete_recipe_details(recipe_details_id: int):
    recipe_detail.pop(recipe_details_id)
    return {"message": "recipe_details deleted"}


# New way to test the operations using these:
def test_create_recipe_details():
    response = client.post("/recipe_details/", json={"Name": "Pasta", "Ingredients": ["noodles", "sauce"], "Instructions": "Boil noodles and add sauce.", "Image": "http://example.com/image.jpg"})
    assert response.status_code == 200
    assert response.json() == [{"Name": "Pasta", "Ingredients": ["noodles", "sauce"], "Instructions": "Boil noodles and add sauce.", "Image": "http://example.com/image.jpg"}]

def test_read_recipe_details():
    response = client.get("/recipe_details/")
    assert response.status_code == 200
    assert response.json() == [{"Name": "Pasta", "Ingredients": ["noodles", "sauce"], "Instructions": "Boil noodles and add sauce.", "Image": "http://example.com/image.jpg"}]

def test_update_recipe_details():
    response = client.put("/recipe_details/0", json={"Name": "Spaghetti", "Ingredients": ["spaghetti", "sauce"], "Instructions": "Boil spaghetti and add sauce.", "Image": "http://example.com/image.jpg"})
    assert response.status_code == 200
    assert response.json() == {"Name": "Spaghetti", "Ingredients": ["spaghetti", "sauce"], "Instructions": "Boil spaghetti and add sauce.", "Image": "http://example.com/image.jpg"}

def test_delete_recipe_details():
    response = client.delete("/recipe_details/0")
    assert response.status_code == 200
    assert response.json() == {"message": "recipe_details deleted"}
