import uuid

from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import List, Optional, Dict, Any
import enum
from bson import ObjectId
from typing import List, Optional
import enum


# Custom field for MongoDB ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: Dict[str, Any]) -> Dict[str, Any]:
        field_schema.update(type="string")
        return field_schema


# Enum Classes for Pydantic Models
class CuisineType(str, enum.Enum):
    AMERICAN = "American"
    MEXICAN = "Mexican"
    CHINESE = "Chinese"
    INDIAN = "Indian"
    THAI = "Thai"
    JAPANESE = "Japanese"
    ITALIAN = "Italian"


class MealType(str, enum.Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    Empty = ""


class MealPlanRequestInput(BaseModel):
    user_id: str
    dates: Optional[List[str]]
    userDescription: str
    url: Optional[str] = None



# Pydantic Models
class UserCreate(BaseModel):
    uid: str
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    age: int
    password: str
    created_at: date = date.today()
    updated_at: date = date.today()
    is_active: bool = True
    is_deleted: bool = False


class UserPreferenceCreate(BaseModel):
    user_id: str
    low_carb: bool = False
    high_protein: bool = False
    low_fat: bool = False
    low_sodium: bool = False
    low_calorie: bool = False
    keto: bool = False
    paleo: bool = False
    vegetarian: bool = False
    vegan: bool = False
    pescatarian: bool = False
    allergies: List[str] = []
    preferred_cuisines: List[CuisineType] = []
    restricted_cuisines: List[CuisineType] = []
    preferred_meal_types: List[MealType] = []
    restricted_meal_types: List[MealType] = []
    preferred_ingredients: List[str] = []
    restricted_ingredients: List[str] = []
    created_at: date = date.today()
    updated_at: date = date.today()
    is_active: bool = True
    is_deleted: bool = False


# 12Am date  12PM date =>  week

class MealPlanCreate(BaseModel):  # 07/11/2024 Lunch [Tea, Sandwich]
    user_id: str
    date: date
    meal_type: MealType
    recipe_id: List[str]
    created_at: date
    updated_at: date


class RecipeCreate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    cuisine: CuisineType
    meal_type: MealType
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    source: Optional[str] = None
    calories: Optional[int] = 0
    protein: Optional[int] = 0
    fat: Optional[int] = 0
    sodium: Optional[int] = 0
    carb: Optional[int] = 0
    servings: Optional[int] = 1
    prep_time: Optional[int] = 0
    cook_time: Optional[int] = 0
    total_time: Optional[int] = 0
    difficulty: Optional[int] = 1
    rating: Optional[int] = None
    reviews: List[str] = []
    date_added: date
    date_updated: date
    is_active: bool = True
    is_deleted: bool = False


# Existing Enums
class CuisinePreferenceType(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    NEUTRAL = "neutral"


class WeekType(str, enum.Enum):
    CURRENT = "This week"
    NEXT = "Next week"


# MongoDB Models
class CuisinePreference(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cuisine_type: CuisineType
    preference: CuisinePreferenceType
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DailyMealPlan(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    date: date
    recipes: List[RecipeCreate] = []


class WeeklyMealPlan(BaseModel):
    user_id: str
    meal_id: str
    meal_date: date
    days: List[DailyMealPlan]
    saved: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB data to a model-friendly format"""
        if "_id" in data:
            data["id"] = str(data.pop("_id"))  # Convert `_id` ObjectId to a string if necessary
        return cls(**data)


class MealTypeSettings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    meal_type: MealType
    is_selected: bool = False
    preferred_time: Optional[str] = None
    dishes_per_meal: int = Field(ge=1, le=6)
    portions_per_dish: int = Field(ge=1, le=6)


# Main User Document Model
class UserDocument(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schemas_examples={
            "example": {
                "uid": "user123",
                "email": "user@example.com",
                "cuisine_preferences": [
                    {
                        "cuisine_type": "ITALIAN",
                        "preference": "LIKE",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ],
                "meal_type_settings": [
                    {
                        "meal_type": "DINNER",
                        "is_selected": True,
                        "preferred_time": "19:00",
                        "dishes_per_meal": 3,
                        "portions_per_dish": 2
                    }
                ]
            }
        }
    )

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uid: str
    email: EmailStr

    # Preferences
    low_carb: bool = False
    high_protein: bool = False
    low_fat: bool = False
    low_sodium: bool = False
    low_calorie: bool = False
    keto: bool = False
    paleo: bool = False
    vegetarian: bool = False
    vegan: bool = False
    pescatarian: bool = False

    # Lists
    allergies: List[str] = []
    preferred_ingredients: List[str] = []
    restricted_ingredients: List[str] = []

    # Nested documents
    cuisine_preferences: List[CuisinePreference] = []
    meal_type_settings: List[MealTypeSettings] = []
    weekly_meal_plans: List[WeeklyMealPlan] = []

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    is_deleted: bool = False


# Recipe Document Model
class RecipeDocument(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    cuisine: CuisineType
    meal_type: MealType
    nutrition: Dict[str, int] = Field(
        default_factory=lambda: {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "sodium": 0,
            "carb": 0
        }
    )
    image_url: str
    video_url: Optional[str] = None
    source: Optional[str] = None
    tags: List[str] = []
    allergens: List[str] = []
    metrics: Dict[str, int] = Field(
        default_factory=lambda: {
            "servings": 0,
            "prep_time": 0,
            "cook_time": 0,
            "total_time": 0,
            "difficulty": 0,
            "rating": 0
        }
    )
    reviews: List[str] = []
    date_added: datetime = Field(default_factory=datetime.now)
    date_updated: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    is_deleted: bool = False


# Final Recap Model
class MealPlanRecap(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str
    date_range: Dict[str, date] = Field(
        default_factory=lambda: {
            "start_date": None,
            "end_date": None
        }
    )
    selected_meals: Dict[str, List[str]] = Field(default_factory=dict)
    portion_settings: Dict[MealType, MealTypeSettings] = Field(default_factory=dict)
    cuisine_preferences: List[CuisinePreference] = []
    dietary_restrictions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
