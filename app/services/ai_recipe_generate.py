from datetime import datetime, timedelta, date
from http.client import HTTPException
import os
import uuid
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from types import SimpleNamespace

from app.database.db_connect import meal_plans_collection
from app.models.models import WeeklyMealPlan, DailyMealPlan, MealType, RecipeCreate
from app.services.services import UserPreferenceService

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(model="gpt-4o")
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = llm
llm.api_key = openai_api_key
Settings.embed_model = embed_model

DEFAULT_CUISINE = "American"  # Default fallback cuisine


def generate_preferences_template(user_preferences):
    user_preferences = SimpleNamespace(**user_preferences)
    preferences = []

    # Dietary attributes as booleans
    if getattr(user_preferences, 'low_carb', False): preferences.append("Low Carb: True")
    if getattr(user_preferences, 'high_protein', False): preferences.append("High Protein: True")
    if getattr(user_preferences, 'low_fat', False): preferences.append("Low Fat: True")
    if getattr(user_preferences, 'low_sodium', False): preferences.append("Low Sodium: True")
    if getattr(user_preferences, 'low_calorie', False): preferences.append("Low Calorie: True")
    if getattr(user_preferences, 'keto', False): preferences.append("Keto: True")
    if getattr(user_preferences, 'paleo', False): preferences.append("Paleo: True")
    if getattr(user_preferences, 'vegetarian', False): preferences.append("Vegetarian: True")
    if getattr(user_preferences, 'vegan', False): preferences.append("Vegan: True")
    if getattr(user_preferences, 'pescatarian', False): preferences.append("Pescatarian: True")

    # Lists
    if getattr(user_preferences, 'allergies', []):
        preferences.append(f"Allergies: {', '.join(user_preferences.allergies)}")
    if getattr(user_preferences, 'preferred_cuisines', []):
        preferences.append(f"Preferred Cuisines: {', '.join([c.value for c in user_preferences.preferred_cuisines])}")
    if getattr(user_preferences, 'restricted_cuisines', []):
        preferences.append(f"Restricted Cuisines: {', '.join([c.value for c in user_preferences.restricted_cuisines])}")
    if getattr(user_preferences, 'preferred_meal_types', []):
        preferences.append(
            f"Preferred Meal Types: {', '.join([m.value for m in user_preferences.preferred_meal_types])}")
    if getattr(user_preferences, 'restricted_meal_types', []):
        preferences.append(
            f"Restricted Meal Types: {', '.join([m.value for m in user_preferences.restricted_meal_types])}")
    if getattr(user_preferences, 'preferred_ingredients', []):
        preferences.append(f"Preferred Ingredients: {', '.join(user_preferences.preferred_ingredients)}")
    if getattr(user_preferences, 'restricted_ingredients', []):
        preferences.append(f"Restricted Ingredients: {', '.join(user_preferences.restricted_ingredients)}")

    return "\n".join(preferences)


class AIGenerateMealPlan:
    @staticmethod
    def _convert_date_to_datetime(d: date) -> datetime:
        return datetime.combine(d, datetime.min.time())

    @staticmethod
    def _prepare_for_mongodb(obj: dict) -> dict:
        for key, value in obj.items():
            if isinstance(value, date):
                obj[key] = AIGenerateMealPlan._convert_date_to_datetime(value)
            elif isinstance(value, list):
                obj[key] = [
                    AIGenerateMealPlan._prepare_for_mongodb(item) if isinstance(item, dict)
                    else AIGenerateMealPlan._convert_date_to_datetime(item) if isinstance(item, date)
                    else item
                    for item in value
                ]
            elif isinstance(value, dict):
                obj[key] = AIGenerateMealPlan._prepare_for_mongodb(value)
        return obj

    @staticmethod
    def _create_fallback_recipe(meal_type: MealType) -> RecipeCreate:
        """Create a fallback recipe when recipe generation fails."""
        current_time = datetime.now()
        return RecipeCreate(
            title=f"Simple {meal_type.value} Recipe",
            description=f"A basic {meal_type.value.lower()} recipe",
            ingredients=["ingredient 1", "ingredient 2"],
            instructions=["step 1", "step 2"],
            meal_type=meal_type,
            cuisine=DEFAULT_CUISINE,  # Use default cuisine instead of None
            created_at=current_time,
            updated_at=current_time,
            date_added=current_time.date(),
            date_updated=current_time.date()
        )

    @staticmethod
    async def generate_meal_plan(user_id: str, start_date: str, user_description: str,
                                 url: Optional[str] = None) -> dict:
        user_preferences = await UserPreferenceService.get_preferences(user_id)
        preference_list = generate_preferences_template(user_preferences)

        current_date = datetime.fromisoformat(start_date)
        used_recipes = set()
        daily_plans = []
        previous_day_recipes = {meal_type: None for meal_type in MealType}

        for day_offset in range(7):
            day_date = current_date + timedelta(days=day_offset)
            daily_recipes = []
            for meal_type in MealType:
                try:
                    if url:
                        recipes = AIGenerateMealPlan._scrape_recipes(url)
                        recipe = AIGenerateMealPlan._get_unique_recipe(
                            recipes, used_recipes, meal_type, preference_list
                        )
                    else:
                        previous_recipe = previous_day_recipes[meal_type] if day_offset > 0 else None
                        recipe = await AIGenerateMealPlan._generate_unique_recipe(
                            meal_type, preference_list, previous_recipe
                        )
                except Exception as e:
                    print(f"Error generating recipe: {e}")
                    recipe = AIGenerateMealPlan._create_fallback_recipe(meal_type)

                daily_recipes.append(recipe)
                used_recipes.add(recipe.title)
                previous_day_recipes[meal_type] = recipe

            daily_plan = DailyMealPlan(
                date=day_date.date(),
                recipes=daily_recipes
            )
            daily_plans.append(daily_plan)

        weekly_meal_plan = WeeklyMealPlan(
            user_id=user_id,
            meal_id=str(uuid.uuid4()),
            meal_date=current_date.date(),
            days=daily_plans,
            saved=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        meal_plan_dict = weekly_meal_plan.model_dump()
        prepared_dict = AIGenerateMealPlan._prepare_for_mongodb(meal_plan_dict)
        await meal_plans_collection.insert_one(prepared_dict)
        meal_plan_dict = meal_plan_dict.pop("_id")
        return meal_plan_dict

    @staticmethod
    async def _generate_unique_recipe(
            meal_type: MealType,
            preference_list: str,
            previous_recipe: Optional[RecipeCreate] = None
    ) -> RecipeCreate:
        context = ""
        if previous_recipe:
            context = f"Previous day's {meal_type.value}: {previous_recipe.title} with ingredients {', '.join(previous_recipe.ingredients)}. "

        prompt = (
            f"{context}Generate a unique {meal_type.value} recipe for today with ingredients "
            f"based on the following user preferences:\n{preference_list}\n\n"
            f"Response should be a JSON object with the following structure:\n"
            "{\n"
            '  "title": "Recipe Title",\n'
            '  "description": "Brief description of the recipe",\n'
            '  "ingredients": ["ingredient 1", "ingredient 2", ...],\n'
            '  "instructions": ["step 1", "step 2", ...],\n'
            '  "cuisine": "American"  // Must be one of: American, Mexican, Chinese, Indian, Thai, Japanese, Italian\n'
            "}"
        )

        messages = [ChatMessage(role="user", content=prompt)]
        response = await llm.achat(messages)

        try:
            recipe_dict = eval(response.message.content)
            current_time = datetime.now()

            return RecipeCreate(
                title=recipe_dict["title"],
                description=recipe_dict["description"],
                ingredients=recipe_dict["ingredients"],
                instructions=recipe_dict["instructions"],
                meal_type=meal_type,
                cuisine=recipe_dict.get("cuisine", DEFAULT_CUISINE),
                created_at=current_time,
                updated_at=current_time,
                date_added=current_time.date(),
                date_updated=current_time.date()
            )
        except Exception as e:
            print(f"Error parsing recipe response: {e}")
            raise

    @staticmethod
    def _scrape_recipes(url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        recipes = soup.find_all('div', class_='recipe')
        current_time = datetime.now()

        return [{
            "title": recipe.find('h2').text,
            "description": recipe.find('p', class_='description').text if recipe.find('p',
                                                                                      class_='description') else f"A delicious {recipe.find('h2').text}",
            "ingredients": [i.text for i in recipe.find('ul').find_all('li')],
            "instructions": [i.text for i in recipe.find('ol').find_all('li')],
            "cuisine": DEFAULT_CUISINE,
            "created_at": current_time,
            "updated_at": current_time,
            "date_added": current_time.date(),
            "date_updated": current_time.date()
        } for recipe in recipes]

    @staticmethod
    def _matches_preferences(recipe: RecipeCreate, user_preferences, meal_type: MealType) -> bool:
        return (
                recipe.meal_type == meal_type and
                all(ingredient not in user_preferences.restricted_ingredients for ingredient in recipe.ingredients) and
                recipe.cuisine not in user_preferences.restricted_cuisines and
                meal_type not in user_preferences.restricted_meal_types
        )

    @staticmethod
    async def get_meal_plan(user_id: str, meal_plan_id: str) -> dict:
        meal_plan = await meal_plans_collection.find_one({"user_id": user_id, "meal_id": meal_plan_id})
        if not meal_plan:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        meal_plan.pop("_id")
        return meal_plan

    @classmethod
    def _get_unique_recipe(cls, recipes, used_recipes, meal_type, preference_list):
        for recipe in recipes:
            if recipe['title'] not in used_recipes:
                current_time = datetime.now()
                recipe_create = RecipeCreate(
                    title=recipe['title'],
                    description=recipe.get('description', f"A delicious {recipe['title']}"),
                    ingredients=recipe['ingredients'],
                    instructions=recipe['instructions'],
                    meal_type=meal_type,
                    cuisine=recipe.get('cuisine', DEFAULT_CUISINE),
                    created_at=current_time,
                    updated_at=current_time,
                    date_added=current_time.date(),
                    date_updated=current_time.date()
                )
                if cls._matches_preferences(recipe_create, preference_list, meal_type):
                    return recipe_create
        return cls._create_fallback_recipe(meal_type)
