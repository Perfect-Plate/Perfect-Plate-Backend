from datetime import datetime
from http.client import HTTPException
from typing import Optional, Dict, Any
from fastapi.encoders import jsonable_encoder

from bson import ObjectId
from fastapi import APIRouter
from pydantic import ValidationError

from app.database.db_connect import meal_plans_collection
from app.models.models import WeeklyMealPlan, RecipeCreate, PyObjectId, MealType
from app.services.ai_recipe_generate import AIGenerateMealPlan
from app.services.services import UserService

openapi = APIRouter()


def serialize_meal(meal):
    if isinstance(meal, dict):
        return {k: serialize_meal(v) for k, v in meal.items()}
    elif isinstance(meal, list):
        return [serialize_meal(i) for i in meal]
    elif isinstance(meal, ObjectId):
        return str(meal)
    return meal


@openapi.get("/")
async def root():
    return {"message": "Project start"}


@openapi.get("ai/get_meal_plan/", response_model=dict)
async def get_meal_plan(user_id: str, meal_plan_id: str):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    meal_plan = await AIGenerateMealPlan.get_meal_plan(user_id, meal_plan_id)
    return serialize_meal(meal_plan)


@openapi.post("/ai/create_meal_plan/", response_model=dict)
async def generate_meal_plan(user_id: str, start_date: str, user_description: str, url: Optional[str] = ""):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    meal_plan = await AIGenerateMealPlan.generate_meal_plan(user_id, start_date, user_description, url)
    return serialize_meal(meal_plan)


# @openapi.put("/ai/update_meal_plan/", response_model=dict)
# async def update_meal_plan(user_id: str, meal_id: str, recipe_id: str, updated_recipe: Dict[str, Any]):
#     user = await UserService.get_user(user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     if not recipe_id:
#         raise HTTPException(status_code=400, detail="Updated recipe data is required to update the recipe")
#
#     try:
#         # Fetch the meal plan using meal_id
#         meal_plan = await meal_plans_collection.find_one({
#             "user_id": user_id,
#             "meal_id": meal_id
#         })
#
#         if not meal_plan:
#             raise HTTPException()
#
#         # Search for the recipe in the meal plan
#         recipe_found = False
#         recipe_id = ObjectId(recipe_id)
#         for day in meal_plan.get("days", []):
#             for recipe in day.get("recipes", []):
#                 if recipe.get("id") == recipe_id:
#                     # Update the recipe and mark it as found
#                     recipe.update(updated_recipe)
#                     recipe["id"] = recipe_id
#                     recipe["date_updated"] = datetime.now()
#                     recipe_found = True
#                     break
#             if recipe_found:
#                 break
#
#         if not recipe_found:
#             raise HTTPException()
#
#         # Update the updated_at timestamp for the meal plan
#         meal_plan["updated_at"] = datetime.now()
#
#         # Replace the entire meal plan document in the database
#         update_result = await meal_plans_collection.replace_one(
#             {"user_id": user_id, "meal_id": meal_id},
#             meal_plan
#         )
#
#         # Return the updated meal plan
#         return serialize_meal(meal_plan)
#
#     except Exception as e:
#         raise HTTPException(e)


@openapi.delete("/ai/delete_meal_plan/", response_model=dict)
async def delete_meal_plan(user_id: str, meal_id: str):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await meal_plans_collection.delete_one({"user_id": user_id, "meal_id": meal_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return {"detail": "Meal plan deleted successfully"}


@openapi.post("/ai/generate_recipe/", response_model=dict)
async def generate_recipe(user_id: str, user_description: str, meal_type: MealType, url: Optional[str] = ""):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recipe = await AIGenerateMealPlan.generate_recipe(user_id, user_description, meal_type, url)
    return serialize_meal(recipe)


@openapi.post("/ai/regenerate_recipe/", response_model=dict)
async def regenerate_recipe(user_id: str, recipe_id: str, meal_type: MealType, meal_plan_id: Optional[str] = ""):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recipe = await AIGenerateMealPlan.regenerate_recipe(user_id, recipe_id, meal_type, meal_plan_id)
    return serialize_meal(recipe)
