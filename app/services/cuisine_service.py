from bson import ObjectId
from fastapi import HTTPException
from app.models.models import CuisinePreference
from app.database.db_connect import preferences_collection
from app.services.services import convert_dates


class CuisinePreferenceService:
    @staticmethod
    async def create_cuisine_preference(user_id: str, preference: CuisinePreference):
        preference_data = convert_dates(preference.dict())
        preference_data["user_id"] = user_id
        result = await preferences_collection.insert_one(preference_data)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create cuisine preference")
        return preference_data

    @staticmethod
    async def update_cuisine_preference(user_id: str, preference_id: str, preference: CuisinePreference):
        preference_data = convert_dates(preference.dict())
        result = await preferences_collection.update_one(
            {"user_id": user_id, "_id": ObjectId(preference_id)},
            {"$set": preference_data}
        )
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to update cuisine preference")
        return preference_data

    @staticmethod
    async def get_cuisine_preferences(user_id: str):
        preferences = await preferences_collection.find({"user_id": user_id}).to_list(length=None)
        if not preferences:
            raise HTTPException(status_code=404, detail="No cuisine preferences found")
        return preferences

    @staticmethod
    async def delete_cuisine_preference(user_id: str, preference_id: str):
        result = await preferences_collection.delete_one({"user_id": user_id, "_id": ObjectId(preference_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Cuisine preference not found")
        return {"detail": "Cuisine preference deleted successfully"}
