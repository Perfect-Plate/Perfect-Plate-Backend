from fastapi import APIRouter, HTTPException

from app.services.cuisine_service import CuisinePreferenceService
from app.services.services import UserService, UserPreferenceService
from app.services.mealplan_service import MealPlanService
from app.models.models import UserCreate, UserPreferenceCreate, MealPlanCreate, CuisinePreference
from typing import List

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Project start"}


@router.post("/create/", response_model=UserCreate)
async def create_user(user: UserCreate):
    return await UserService.create_user(user)


@router.get("/users/{user_id}/", response_model=UserCreate)
async def get_user(user_id: str):
    return await UserService.get_user(user_id)


@router.put("/users/{user_id}/", response_model=UserCreate)
async def update_user(user_id: str, user: UserCreate):
    return await UserService.update_user(user_id, user)


@router.delete("/users/{user_id}/")
async def delete_user(user_id: str):
    return await UserService.delete_user(user_id)


@router.post("/users/{user_id}/preferences/", response_model=UserPreferenceCreate)
async def create_user_preferences(user_id: str, preferences: UserPreferenceCreate):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await UserPreferenceService.create_preference(user_id, preferences)


@router.put("/users/{user_id}/preferences/", response_model=UserPreferenceCreate)
async def update_user_preferences(user_id: str, preferences: UserPreferenceCreate):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await UserPreferenceService.update_preference(user_id, preferences)


@router.get("/users/{user_id}/preferences/", response_model=UserPreferenceCreate)
async def get_user_preferences(user_id: str):
    return await UserPreferenceService.get_preferences(user_id)


@router.post("/users/{user_id}/meal-plans/", response_model=dict)
async def create_meal_plan(user_id: str, meal_plan: MealPlanCreate):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await MealPlanService.create_meal_plan(user_id, meal_plan)


@router.put("/users/{user_id}/meal-plans/", response_model=dict)
async def update_meal_plan(user_id: str, meal_plan: MealPlanCreate):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await MealPlanService.update_meal_plan(user_id, meal_plan)


@router.get("/users/{user_id}/meal-plans/", response_model=List[dict])
async def get_user_meal_plans(user_id: str):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await MealPlanService.get_user_meal_plans(user_id)


@router.get("/users/{user_id}/meal-plan/{meal_plan_id}/", response_model=dict)
async def get_user_meal_plan(user_id: str, meal_plan_id: str):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await MealPlanService.get_user_meal_plan(user_id, meal_plan_id)


@router.delete("/users/{user_id}/meal-plan/{meal_plan_id}/")
async def delete_user_meal_plan(user_id: str, meal_plan_id: str):
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await MealPlanService.delete_user_meal_plan(user_id, meal_plan_id)


@router.post("/users/{user_id}/cuisine/preference/", response_model=dict)
async def create_cuisine_preference(user_id: str, preference: CuisinePreference):
    return await CuisinePreferenceService.create_cuisine_preference(user_id, preference)


@router.put("/users/{user_id}/cuisine/preference/{preference_id}/", response_model=dict)
async def update_cuisine_preference(user_id: str, preference_id: str, preference: CuisinePreference):
    return await CuisinePreferenceService.update_cuisine_preference(user_id, preference_id, preference)


@router.get("/users/{user_id}/cuisine/preferences/", response_model=List[dict])
async def get_cuisine_preferences(user_id: str):
    return await CuisinePreferenceService.get_cuisine_preferences(user_id)


@router.delete("/users/{user_id}/cuisine/preference/{preference_id}/")
async def delete_cuisine_preference(user_id: str, preference_id: str):
    return await CuisinePreferenceService.delete_cuisine_preference(user_id, preference_id)