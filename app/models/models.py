from pydantic import BaseModel
from datetime import date
from typing import List, Optional
import enum


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
    SNACK = "Snack"


# Pydantic Models
class UserCreate(BaseModel):
    uid: str
    email: str


class UserPreferenceCreate(BaseModel):
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


class MealPlanCreate(BaseModel):
    date: date
    meal_type: MealType
    recipe_id: int
