from sqlalchemy.orm import Session
from sqlalchemy.testing.pickleable import User
from fastapi import HTTPException

from app.database.db_connect import client
from app.models.models import UserCreate, UserPreferenceCreate, MealPlanCreate


class UserService:
    @staticmethod
    async def create_user(user: UserCreate) -> User:
        print(user)
        # Use Supabase client to insert a new user
        response = client.table("users").insert({"uid": user.uid, "email": user.email}).execute()  # Await the call
        print(response)
        if response:
            raise HTTPException(status_code=500, detail="Failed to create user")
        return response  # Return the created user data

    @staticmethod
    async def get_user(user_id: int):  # Make this method async
        response = await client.table("users").select("*").filter("id", "eq", user_id).execute()  # Await the call
        if response.status_code != 200 or not response.data:
            return None  # Or raise an HTTPException if preferred
        return response.data[0]  # Return the first matching user



class UserPreferenceService:
    @staticmethod
    def create_preference(db: Session, user_id: int, preferences: UserPreferenceCreate):
        db_preferences = UserPreferenceService(
        )
        db.add(db_preferences)
        db.commit()
        db.refresh(db_preferences)
        return db_preferences

    @staticmethod
    def get_preferences(user_id: int):
        return client.table.query(UserPreferenceService).filter(UserPreferenceService.user_id == user_id).first()


class MealPlanService:
    @staticmethod
    def create_meal_plan(db: Session, user_id: int, meal_plan: MealPlanCreate):
        db_meal_plan = MealPlanService(
        )
        db.add(db_meal_plan)
        db.commit()
        db.refresh(db_meal_plan)
        return db_meal_plan

    @staticmethod
    def get_user_meal_plans(db: Session, user_id: int):
        return db.query(MealPlanService).filter(MealPlanService.user_id == user_id).all()
