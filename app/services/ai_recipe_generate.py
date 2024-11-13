from datetime import datetime, timedelta, date
from http.client import HTTPException

import os
import uuid
from random import random
from typing import Dict, Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from llama_index.core.prompts import ChatPromptTemplate
from llama_cloud.types import llm
from llama_index.core.query_pipeline import QueryPipeline as QP

from app.database.db_connect import meal_plans_collection
from app.models.models import WeeklyMealPlan, DailyMealPlan, MealType, RecipeCreate
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from types import SimpleNamespace

from app.services.services import UserPreferenceService

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(model="gpt-4o")
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = llm
llm.api_key = openai_api_key
Settings.embed_model = embed_model


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

    # Lists (show only if they contain items)
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

    # Combine into a single string
    return "\n".join(preferences)


def scrape_recipes(url: str):
    # Scrape the website and get the recipes
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    recipes = soup.find_all('div', class_='recipe')
    recipe_list = []
    for recipe in recipes:
        title = recipe.find('h2').text
        ingredients = recipe.find('ul').find_all('li')
        ingredient_list = [ingredient.text for ingredient in ingredients]
        instructions = recipe.find('ol').find_all('li')
        instruction_list = [instruction.text for instruction in instructions]
        recipe_list.append({
            "title": title,
            "ingredients": ingredient_list,
            "instructions": instruction_list
        })
    return recipe_list


class AIGenerateMealPlan:

    @staticmethod
    def _convert_date_to_datetime(d: date) -> datetime:
        """Convert a date object to datetime object set to midnight."""
        return datetime.combine(d, datetime.min.time())

    @staticmethod
    def _prepare_for_mongodb(obj: dict) -> dict:
        """Recursively convert all date objects to datetime objects in a dictionary."""
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
    async def generate_meal_plan(user_id: str, start_date: str, user_description: str, url: str) -> dict:
        user_preferences = await UserPreferenceService.get_preferences(user_id)
        preference_list = generate_preferences_template(user_preferences)

        current_date = datetime.fromisoformat(start_date)
        used_recipes = set()  # Keep track of used recipes

        daily_plans = []
        previous_day_recipes = {meal_type: None for meal_type in [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]}

        for day_offset in range(7):
            day_date = current_date + timedelta(days=day_offset)
            daily_recipes = []

            for meal_type in [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]:
                if url:
                    # Scrape recipes from the provided URL
                    recipes = scrape_recipes(url)
                    recipe = AIGenerateMealPlan._get_unique_recipe(
                        recipes, used_recipes, user_preferences, meal_type, preference_list
                    )
                else:
                    # Skip the previous day's recipe on the first day
                    if day_offset == 0:
                        recipe = AIGenerateMealPlan._generate_unique_recipe(
                            user_preferences, meal_type, preference_list, None  # No previous recipe for the first day
                        )
                    else:
                        # Pass the previous day's recipe as context on subsequent days
                        previous_recipe = previous_day_recipes[meal_type]
                        recipe = AIGenerateMealPlan._generate_unique_recipe(
                            user_preferences, meal_type, preference_list, previous_recipe
                        )

                daily_recipes.append(recipe)
                used_recipes.add(recipe.title)  # Add the recipe to the used recipes set
                previous_day_recipes[meal_type] = recipe  # Store for next day's context

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
        weekly_meal_plan = await meal_plans_collection.insert_one(prepared_dict)
        return weekly_meal_plan.model_dump()

    @staticmethod
    def _generate_unique_recipe(user_preferences, meal_type, preference_list, previous_recipe):
        # Generate a new recipe that matches user preferences, incorporating the previous day's meal as context if
        # available
        context = f"Previous day's {meal_type.value}: {previous_recipe.title} with ingredients {', '.join(previous_recipe.ingredients)}." if previous_recipe else ""
        prompt = (f"{context} Generate a unique {meal_type.value} recipe for today with different ingredients "
                  f"based on the following user preferences:\n{preference_list}. "
                  f"consider user_preferences: \n{user_preferences}(\n"
                  )

        sllm = llm.as_structured_llm(output_cls=RecipeCreate)
        chat_prompt_tmpl = ChatPromptTemplate(
            message_templates=[
                ChatMessage.from_str(
                    prompt,
                    role="user"
                )
            ]
        )

        qp = QP(chain=[chat_prompt_tmpl, sllm])
        try:
            recipe = qp.run()
        except Exception as e:
            print(f"Error during query pipeline execution: {e}")
            raise

        print(f"Generated {meal_type.value}: {recipe}")
        return recipe

    @staticmethod
    def _matches_preferences(recipe, user_preferences, meal_type):
        # Check if the recipe matches the user's dietary preferences and restrictions
        return (recipe.meal_type == meal_type and
                all(ingredient not in user_preferences.restricted_ingredients for ingredient in recipe.ingredients) and
                all(cuisine not in user_preferences.restricted_cuisines for cuisine in [recipe.cuisine]) and
                all(meal_type not in user_preferences.restricted_meal_types))

    @staticmethod
    async def get_meal_plan(user_id: str, meal_plan_id: str) -> Dict[str, Any]:
        meal_plan = await meal_plans_collection.find_one({"user_id": user_id, "meal_id": meal_plan_id})
        if not meal_plan:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        return meal_plan

    @classmethod
    def _get_unique_recipe(cls, recipes, used_recipes, user_preferences, meal_type, preference_list):
        # Get a unique recipe from the list of scraped recipes
        for recipe in recipes:
            if recipe['title'] not in used_recipes:
                recipe_create = RecipeCreate(
                    title=recipe['title'],
                    ingredients=recipe['ingredients'],
                    instructions=recipe['instructions'],
                    meal_type=meal_type,
                    cuisine=meal_type,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                if cls._matches_preferences(recipe_create, user_preferences, meal_type):
                    return recipe_create
        return cls._generate_unique_recipe(user_preferences, meal_type, preference_list)

