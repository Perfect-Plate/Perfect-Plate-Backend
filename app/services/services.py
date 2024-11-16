from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from datetime import datetime, date  # Add date to the import

from app.database.db_connect import users_collection, preferences_collection, meal_plans_collection
from app.models.models import UserCreate, UserPreferenceCreate, MealPlanCreate, UserDocument, WeeklyMealPlan


# Utility function to handle date conversions
def convert_dates(data):
    for key, value in data.items():
        if isinstance(value, date):  # Use `date` directly here
            data[key] = datetime.combine(value, datetime.min.time())
    return data


# MongoDB Index Creation
async def create_indexes(db):
    await db.users.create_index("email", unique=True)
    await db.users.create_index("uid", unique=True)
    await db.recipes.create_index([("title", "text"), ("description", "text")])
    await db.recipes.create_index([("cuisine", 1), ("meal_type", 1)])


# Service Classes
class UserService:
    @staticmethod
    async def create_user(user: UserCreate):
        user_data = convert_dates(user.dict())
        try:
            result = await users_collection.insert_one(user_data)
            if not result.inserted_id:
                raise HTTPException(status_code=500, detail="Failed to create user")
            return user_data
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

    @staticmethod
    async def get_user(user_id: str):
        user = await users_collection.find_one({"uid": user_id, "is_active": True, "is_deleted": False})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    async def update_user(user_id: str, user: UserCreate):
        user_data = convert_dates(user.dict())
        result = await users_collection.update_one({"uid": user_id}, {"$set": user_data})
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to update user")
        return user_data

    @staticmethod
    async def delete_user(user_id: str):
        result = await users_collection.update_one({"uid": user_id}, {"$set": {"is_active": False}, "is_deleted": True})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": "User deleted successfully"}


class UserPreferenceService:
    @staticmethod
    async def create_preference(user_id: str, preferences: UserPreferenceCreate):
        pref_data = convert_dates(preferences.dict())
        pref_data["user_id"] = user_id
        result = await preferences_collection.insert_one(pref_data)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create user preferences")
        return pref_data

    @staticmethod
    async def update_preference(user_id: str, preferences: UserPreferenceCreate):
        pref_data = convert_dates(preferences.dict())
        result = await preferences_collection.update_one({"user_id": user_id}, {"$set": pref_data})
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to update user preferences")
        return pref_data

    @staticmethod
    async def get_preferences(user_id: str) -> UserPreferenceCreate:
        preferences = await preferences_collection.find_one({"user_id": user_id})
        if preferences is None:
            raise HTTPException(status_code=404, detail="Preferences not found")
        return preferences


