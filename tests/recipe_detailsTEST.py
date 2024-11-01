from fastapi.testclient import TestClient
from app.models.recipe_details import app

client = TestClient(app)

# TEST FILE FOR RECIPE_DETAILS DATACLASS CRUD OPERATIONS

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
