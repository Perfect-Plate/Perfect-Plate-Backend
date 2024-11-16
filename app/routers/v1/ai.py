from http.client import HTTPException
from typing import Optional

from fastapi import APIRouter

from app.models.models import WeeklyMealPlan
from app.services.ai_recipe_generate import AIGenerateMealPlan
from app.services.services import UserService

openapi = APIRouter()


@openapi.get("/")
async def root():
    return {"message": "Project start"}


@openapi.get("ai/get_meal_plan/", response_model=dict)
async def get_meal_plan(user_id: str, meal_plan_id: str):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await AIGenerateMealPlan.get_meal_plan(user_id, meal_plan_id)


@openapi.post("/ai/create_meal_plan/", response_model=dict)
async def generate_meal_plan(user_id: str, start_date: str, user_description: str, url: Optional[str] = ""):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await AIGenerateMealPlan.generate_meal_plan(user_id, start_date, user_description, url)
