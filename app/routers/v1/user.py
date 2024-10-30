from fastapi import HTTPException, Depends, APIRouter, FastAPI
from sqlalchemy.orm import Session

from app.services.services import UserService, UserPreferenceService, MealPlanService
from app.models.models import UserCreate, UserPreferenceCreate, MealPlanCreate
from app.database.db_connect import get_db, SessionDep  # Import the get_db function
from typing import List

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Project start"}


@router.post("/create/")
def create_user(user: UserCreate, session: SessionDep) -> dict:
    print(user)
    return UserService.create_user(session, user)


@router.post("/users/{user_id}/preferences/", response_model=dict)
def create_user_preferences(
        user_id: int,
        preferences: UserPreferenceCreate,
        db: Session = Depends(get_db)
):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPreferenceService.create_preference(db, user_id, preferences)


@router.get("/users/{user_id}/preferences/", response_model=dict)
def get_user_preferences(user_id: int, db: Session = Depends(get_db)):
    preferences = UserPreferenceService.get_preferences(db, user_id)
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return preferences


@router.post("/users/{user_id}/meal-plans/", response_model=dict)
def create_meal_plan(
        user_id: int,
        meal_plan: MealPlanCreate,
        db: Session = Depends(get_db)
):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return MealPlanService.create_meal_plan(db, user_id, meal_plan)


@router.get("/users/{user_id}/meal-plans/", response_model=List[dict])
def get_user_meal_plans(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return MealPlanService.get_user_meal_plans(db, user_id)
