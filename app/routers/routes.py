from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from ..services.services import UserService, PreferenceService, MealPlanService
from ..models.models import UserCreate, UserPreferenceCreate, MealPlanCreate
from app.database.db_connect import get_db  # Import the get_db function
from typing import List

app = FastAPI(title="PerfectPlates API")


@app.post("/users/", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user)


@app.post("/users/{user_id}/preferences/", response_model=dict)
def create_user_preferences(
        user_id: int,
        preferences: UserPreferenceCreate,
        db: Session = Depends(get_db)
):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return PreferenceService.create_preference(db, user_id, preferences)


@app.get("/users/{user_id}/preferences/", response_model=dict)
def get_user_preferences(user_id: int, db: Session = Depends(get_db)):
    preferences = PreferenceService.get_preferences(db, user_id)
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return preferences


@app.post("/users/{user_id}/meal-plans/", response_model=dict)
def create_meal_plan(
        user_id: int,
        meal_plan: MealPlanCreate,
        db: Session = Depends(get_db)
):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return MealPlanService.create_meal_plan(db, user_id, meal_plan)


@app.get("/users/{user_id}/meal-plans/", response_model=List[dict])
def get_user_meal_plans(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return MealPlanService.get_user_meal_plans(db, user_id)
