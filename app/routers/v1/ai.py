from datetime import datetime
from http.client import HTTPException
from typing import Optional, Dict, Any
from fastapi.encoders import jsonable_encoder

from bson import ObjectId
from fastapi import APIRouter
from pydantic import ValidationError

from app.database.db_connect import meal_plans_collection
from app.models.models import WeeklyMealPlan, RecipeCreate, PyObjectId, MealType, MealPlanRequestInput
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


@openapi.get("/get_meal_plan/", response_model=dict)
async def get_meal_plan(user_id: str, meal_plan_id: str):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    meal_plan = await AIGenerateMealPlan.get_meal_plan(user_id, meal_plan_id)
    return serialize_meal(meal_plan)


@openapi.post("/create_meal_plan/", response_model=dict)
async def generate_meal_plan(input_data: MealPlanRequestInput):
    user = await UserService.get_user(input_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    meal_plan = await AIGenerateMealPlan.generate_meal_plan(input_data)
    return serialize_meal(meal_plan)


@openapi.delete("/delete_meal_plan/", response_model=dict)
async def delete_meal_plan(user_id: str, meal_id: str):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await meal_plans_collection.delete_one({"user_id": user_id, "meal_id": meal_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return {"detail": "Meal plan deleted successfully"}


@openapi.post("/generate_recipe/", response_model=dict)
async def generate_recipe(input_data: MealPlanRequestInput):
    user = await UserService.get_user(input_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recipe = await AIGenerateMealPlan.generate_recipe(input_data)
    return serialize_meal(recipe)


@openapi.post("/regenerate_recipe/", response_model=dict)
async def regenerate_recipe(user_id: str, recipe_id: str, meal_plan_id: Optional[str] = ""):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recipe = await AIGenerateMealPlan.regenerate_recipe(user_id, recipe_id, meal_plan_id)
    return serialize_meal(recipe)
