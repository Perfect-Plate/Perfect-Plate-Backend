from fastapi import HTTPException, Depends, APIRouter

from app.services.services import UserService, UserPreferenceService, MealPlanService
from app.models.models import UserCreate, UserPreferenceCreate, MealPlanCreate
from typing import List

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Project start"}


@router.post("/create/", response_model=UserCreate)
async def create_user(user: UserCreate) -> UserCreate:
    db_user = await UserService.create_user(user)  # Await the asynchronous call
    return db_user  # Adjust based on the response structure



@router.post("/users/{user_id}/preferences/", response_model=dict)
def create_user_preferences(
        user_id: int,
        preferences: UserPreferenceCreate
):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPreferenceService.create_preference(user_id, preferences)


@router.get("/users/{user_id}/preferences/", response_model=dict)
def get_user_preferences(user_id: int):
    preferences = UserPreferenceService.get_preferences(user_id)
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return preferences


@router.post("/users/{user_id}/meal-plans/", response_model=dict)
def create_meal_plan(
        user_id: int,
        meal_plan: MealPlanCreate
):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return MealPlanService.create_meal_plan(user_id, meal_plan)


@router.get("/users/{user_id}/meal-plans/", response_model=List[dict])
def get_user_meal_plans(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return MealPlanService.get_user_meal_plans(user_id)
