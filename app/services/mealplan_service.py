from fastapi import HTTPException
from datetime import datetime, date  # Add date to the import
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.database.db_connect import users_collection, preferences_collection, meal_plans_collection
from app.models.models import UserCreate, UserPreferenceCreate, MealPlanCreate, UserDocument, WeeklyMealPlan
from app.services.services import convert_dates


class MealPlanService:
    @staticmethod
    async def create_meal_plan(user_id: str, meal_plan: MealPlanCreate):
        meal_plan_data = convert_dates(meal_plan.dict())
        meal_plan_data["user_id"] = user_id
        result = await meal_plans_collection.insert_one(meal_plan_data)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create meal plan")
        return meal_plan_data

    @staticmethod
    async def update_meal_plan(user_id: str, meal_plan: MealPlanCreate):
        meal_plan_data = convert_dates(meal_plan.dict())
        meal_plan_data["user_id"] = user_id
        result = await meal_plans_collection.update_one(
            {"user_id": user_id},
            {"$set": meal_plan_data}
        )
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to update meal plan")
        return meal_plan_data

    @staticmethod
    async def get_user_meal_plans(user_id: str):
        meal_plans = await meal_plans_collection.find({"user_id": user_id}).to_list(length=100)
        if not meal_plans:
            raise HTTPException(status_code=404, detail="Meal plans not found")
        return meal_plans

    @staticmethod
    async def get_user_meal_plan(user_id: str, meal_plan_id: str):
        meal_plan = await meal_plans_collection.find_one({"user_id": user_id, "_id": ObjectId(meal_plan_id)})
        if meal_plan is None:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        return meal_plan

    @staticmethod
    async def delete_user_meal_plan(user_id: str, meal_plan_id: str):
        result = await meal_plans_collection.delete_one({"user_id": user_id, "_id": ObjectId(meal_plan_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        return {"detail": "Meal plan deleted successfully"}

