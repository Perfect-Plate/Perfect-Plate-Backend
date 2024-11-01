import os
from fastapi import FastAPI
from dotenv import load_dotenv
import asyncpg
from typing import List
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
recipe_detail = []

@dataclass
class RecipeDetails:
    Name: str  # EG: Spaghetti Carbonara
    Ingredients: List[str]  # Array, with each ingredient. As list because each recipe will vary in number of ingredients.
    Instructions: str  # For the instructions.
    Image: str  # Link to image

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


if __name__ == "__main__":
    import uvicorn

    rd = RecipeDetails(Name="banana", Ingredients=["peel,banana,yellow"], Instructions="Peel banana, Eat banana",
                       Image="https://th.bing.com/th/id/R.0f3cc1b69f7046e6355687263aead9ee?rik=e%2fzLRdxmCMtNRA&riu=http%3a%2f%2fupload.wikimedia.org%2fwikipedia%2fcommons%2f6%2f69%2fBanana.png&ehk=0MA9r3huU44GTjIIWGK6A1R0At%2bSPNmztxBBWKsquWw%3d&risl=1&pid=ImgRaw&r=0")

    create_recipe_details(rd)
    uvicorn.run(app, host="0.0.0.0", port=8000)
