from datetime import datetime, timedelta, date
from http.client import HTTPException
import os
import uuid
from typing import Dict, Any, Optional
from bson import ObjectId
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from types import SimpleNamespace

from app.database.db_connect import meal_plans_collection, recipes_collection
from app.models.models import WeeklyMealPlan, DailyMealPlan, MealType, RecipeCreate, CuisineType, MealPlanRequestInput
from app.services.services import UserPreferenceService

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(model="gpt-4")
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = llm
llm.temperature = 0.9
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

    # Lists
    if getattr(user_preferences, 'allergies', []):
        preferences.append(f"Allergies: {', '.join(user_preferences.allergies)}")
    if getattr(user_preferences, 'preferred_cuisines', []):
        # Assuming preferred_cuisines is a list of strings
        preferences.append(f"Preferred Cuisines: {', '.join(user_preferences.preferred_cuisines)}")
    if getattr(user_preferences, 'restricted_cuisines', []):
        # Assuming restricted_cuisines is a list of strings
        preferences.append(f"Restricted Cuisines: {', '.join(user_preferences.restricted_cuisines)}")
    if getattr(user_preferences, 'preferred_meal_types', []):
        # Assuming preferred_meal_types is a list of strings
        preferences.append(f"Preferred Meal Types: {', '.join(user_preferences.preferred_meal_types)}")
    if getattr(user_preferences, 'restricted_meal_types', []):
        # Assuming restricted_meal_types is a list of strings
        preferences.append(f"Restricted Meal Types: {', '.join(user_preferences.restricted_meal_types)}")
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
    async def generate_meal_plan(input_data: MealPlanRequestInput) -> dict:
        user_id = input_data.user_id
        dates = input_data.dates
        url = input_data.url
        user_description = input_data.userDescription

        # Fetch user preferences and prepare preference template
        user_preferences = await UserPreferenceService.get_preferences(user_id)
        preference_list = generate_preferences_template(user_preferences)

        used_recipes = set()  # Keep track of used recipes to avoid repetition
        daily_plans = []  # Store daily meal plans
        previous_day_recipes = {meal_type: None for meal_type in MealType}  # Track recipes for each meal type

        print(dates)

        # Loop through the provided dates
        for date_str in dates:
            try:
                day_date = datetime.fromisoformat(date_str)  # Convert string to datetime
            except ValueError as e:
                print(f"Invalid date format: {date_str}. Error: {e}")
                continue  # Skip invalid dates

            daily_recipes = []  # Store recipes for the current day

            # Generate recipes for each meal type
            for meal_type in MealType:
                try:
                    if url:
                        recipes = await AIGenerateMealPlan._scrape_recipes(url)
                        print(recipes)
                        recipe = await AIGenerateMealPlan._get_unique_recipe(recipes, set(), user_preferences,
                                                                             meal_type, preference_list,
                                                                             user_description, True)
                    else:
                        previous_recipe = previous_day_recipes[meal_type]  # Get the recipe from the previous day
                        recipe = await AIGenerateMealPlan._generate_unique_recipe(
                            meal_type, preference_list, previous_recipe
                        )
                except Exception as e:
                    print(f"Error generating recipe for {meal_type}: {e}")
                    return {"error": "Error generating recipe"}

                daily_recipes.append(recipe)  # Add the recipe to the day's plan
                used_recipes.add(recipe.title)  # Mark the recipe as used
                previous_day_recipes[meal_type] = recipe  # Update the previous recipe for this meal type

            # Create a daily meal plan
            daily_plan = DailyMealPlan(
                date=day_date.date(),
                recipes=daily_recipes
            )
            daily_plans.append(daily_plan)  # Append to the weekly plan

        # Create a weekly meal plan object
        weekly_meal_plan = WeeklyMealPlan(
            user_id=user_id,
            meal_id=str(uuid.uuid4()),
            meal_date=datetime.now().date(),
            days=daily_plans,
            saved=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Prepare and save the meal plan to MongoDB
        meal_plan_dict = weekly_meal_plan.model_dump()
        prepared_dict = AIGenerateMealPlan._prepare_for_mongodb(meal_plan_dict)
        await meal_plans_collection.insert_one(prepared_dict)

        return meal_plan_dict

    @staticmethod
    async def _generate_unique_recipe(
            meal_type: MealType,
            preference_list: str,
            previous_recipe: Optional[RecipeCreate] = None,
            user_description: str = "",
            is_single: bool = False
    ) -> RecipeCreate:
        context = ""

        if is_single:
            prompt = (
                f"Generate a unique recipe for today with different ingredients "
                f"and user description:\n{user_description}\n\n"
                f"based on the following user preferences:\n{preference_list}\n\n"
                f"Response should be a JSON object with the following structure:\n"
                "{\n"
                '  "title": "Recipe Title",\n'
                '  "description": "A description of the recipe",\n'
                '  "ingredients": ["ingredient 1", "ingredient 2", ...],\n'
                '  "instructions": ["step 1", "step 2", ...],\n'
                '  "cuisine": "Mexican|Italian|Chinese|American|Indian|Thai|Japanese",\n'
                '  "calories": 500,\n'
                '  "protein": 30,\n'
                '  "fat": 20,\n'
                '  "sodium": 500,\n'
                '  "carb": 40,\n'
                '  "servings": 4,\n'
                '  "prep_time": 15,\n'
                '  "cook_time": 30,\n'
                '  "difficulty": 2\n'
                "}"
            )
        else:
            if previous_recipe:
                context = f"Previous day's {meal_type.value}: {previous_recipe.title} with ingredients {', '.join(previous_recipe.ingredients)}. "

            prompt = (
                f"{context}Generate a unique {meal_type.value} recipe for today with different ingredients "
                f"and user description:\n{user_description}\n\n"
                f"based on the following user preferences:\n{preference_list}\n\n"
                f"Response should be a JSON object with the following structure:\n"
                "{\n"
                '  "title": "Recipe Title",\n'
                '  "description": "A description of the recipe",\n'
                '  "ingredients": ["ingredient 1", "ingredient 2", ...],\n'
                '  "instructions": ["step 1", "step 2", ...],\n'
                '  "cuisine": "Mexican|Italian|Chinese|American|Indian|Thai|Japanese",\n'
                '  "calories": 500,\n'
                '  "protein": 30,\n'
                '  "fat": 20,\n'
                '  "sodium": 500,\n'
                '  "carb": 40,\n'
                '  "servings": 4,\n'
                '  "prep_time": 15,\n'
                '  "cook_time": 30,\n'
                '  "difficulty": 2\n'
                "}"
            )

        messages = [ChatMessage(role="user", content=prompt)]
        response = await llm.achat(messages)

        try:
            recipe_dict = eval(response.message.content)
            return RecipeCreate(
                title=recipe_dict["title"],
                description=recipe_dict["description"],
                ingredients=recipe_dict["ingredients"],
                instructions=recipe_dict["instructions"],
                meal_type=meal_type,
                cuisine=getattr(CuisineType, recipe_dict.get("cuisine", "AMERICAN").upper(), CuisineType.AMERICAN),
                calories=recipe_dict.get("calories", 0),
                protein=recipe_dict.get("protein", 0),
                fat=recipe_dict.get("fat", 0),
                sodium=recipe_dict.get("sodium", 0),
                carb=recipe_dict.get("carb", 0),
                servings=recipe_dict.get("servings", 1),
                prep_time=recipe_dict.get("prep_time", 0),
                cook_time=recipe_dict.get("cook_time", 0),
                total_time=recipe_dict.get("prep_time", 0) + recipe_dict.get("cook_time", 0),
                difficulty=recipe_dict.get("difficulty", 1),
                date_added=date.today(),
                date_updated=date.today()
            )
        except Exception as e:
            print(f"Error parsing recipe response: {e}")
            # Return a fallback recipe with all required fields
            return RecipeCreate(
                title=f"{meal_type.value} Recipe",
                description=f"A basic {meal_type.value} recipe",
                ingredients=["ingredient 1", "ingredient 2"],
                instructions=["step 1", "step 2"],
                meal_type=meal_type,
                cuisine=CuisineType.AMERICAN,
                calories=0,
                protein=0,
                fat=0,
                sodium=0,
                carb=0,
                servings=1,
                prep_time=0,
                cook_time=0,
                total_time=0,
                difficulty=1,
                date_added=date.today(),
                date_updated=date.today()
            )

    @staticmethod
    async def _scrape_recipes(url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        recipes = soup.find_all('div', class_='recipe')
        return [{
            "title": recipe.find('h2').text,
            "ingredients": [i.text for i in recipe.find('ul').find_all('li')],
            "instructions": [i.text for i in recipe.find('ol').find_all('li')]
        } for recipe in recipes]

    @staticmethod
    def _matches_preferences(recipe: RecipeCreate, user_preferences, meal_type: MealType) -> bool:
        return (
                recipe.meal_type == meal_type and
                all(ingredient not in user_preferences.restricted_ingredients for ingredient in recipe.ingredients) and
                (not recipe.cuisine or recipe.cuisine not in user_preferences.restricted_cuisines) and
                meal_type not in user_preferences.restricted_meal_types
        )

    @staticmethod
    async def get_meal_plan(user_id: str, meal_plan_id: str) -> Dict[str, Any]:
        meal_plan = await meal_plans_collection.find_one({"user_id": user_id, "meal_id": meal_plan_id})
        if not meal_plan:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        return meal_plan

    @classmethod
    def _get_unique_recipe(cls, recipes, used_recipes, user_preferences, meal_type, preference_list,
                           user_description="", is_sigle=False):
        for recipe in recipes:
            if recipe['title'] not in used_recipes:
                recipe_create = RecipeCreate(
                    title=recipe['title'],
                    description=f"A delicious {recipe['title']} recipe",  # Added description
                    ingredients=recipe['ingredients'],
                    instructions=recipe['instructions'],
                    meal_type=meal_type,
                    cuisine=CuisineType.AMERICAN,  # Default cuisine
                    calories=0,
                    protein=0,
                    fat=0,
                    sodium=0,
                    carb=0,
                    servings=1,
                    prep_time=0,
                    cook_time=0,
                    total_time=0,
                    difficulty=1,
                    date_added=date.today(),
                    date_updated=date.today()
                )
                if cls._matches_preferences(recipe_create, user_preferences, meal_type):
                    return recipe_create
        return cls._generate_unique_recipe(meal_type, preference_list, None, user_description, is_sigle)

    @staticmethod
    async def update_recipe_in_meal_plan(
            user_id: str,
            meal_id: str,
            recipe_id: str,
            updated_recipe: Optional[RecipeCreate] = None
    ):
        """
        Update a single recipe within a meal plan by retrieving the whole meal plan,
        searching for the recipe, and updating the entire record.

        Args:
            user_id: ID of the user
            meal_id: ID of the meal plan
            recipe_id: ID of the recipe to update
            updated_recipe: Dictionary containing the updated recipe data

        Returns:
            Dict containing the updated meal plan

        Raises:
            HTTPException: If meal plan is not found or update fails
        """
        if not updated_recipe:
            raise HTTPException()

        try:
            # Fetch the meal plan using meal_id
            meal_plan = await meal_plans_collection.find_one({
                "user_id": user_id,
                "meal_id": meal_id
            })

            if not meal_plan:
                raise HTTPException()

            # Search for the recipe in the meal plan
            recipe_found = False
            for day in meal_plan.get("days", []):
                for recipe in day.get("recipes", []):
                    if recipe.get("id") == recipe_id:
                        # Update the recipe and mark it as found
                        recipe.update(updated_recipe)
                        recipe["date_updated"] = datetime.now()
                        recipe_found = True
                        break
                if recipe_found:
                    break

            if not recipe_found:
                raise HTTPException()

            # Update the updated_at timestamp for the meal plan
            meal_plan["updated_at"] = datetime.now()

            # Replace the entire meal plan document in the database
            update_result = await meal_plans_collection.replace_one(
                {"user_id": user_id, "meal_id": meal_id},
                meal_plan
            )

            if update_result.modified_count == 0:
                raise HTTPException(status_code=400, detail="No changes made to the meal plan")

            # Return the updated meal plan
            return meal_plan

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating recipe: {str(e)}")

    @classmethod
    async def generate_recipe(cls, input_data: MealPlanRequestInput) -> Dict[str, Any]:
        """
        Generate a recipe based on user preferences and a user description.

        Args:
            user_id: ID of the user
            user_description: Description of the user
            url: URL to scrape recipes from

        Returns:
            Dict containing the generated recipe data or an error message
            :param input_data:
        """
        user_id = input_data.user_id
        # dates = input_data.dates
        url = input_data.url
        user_description = input_data.userDescription

        user_preferences = await UserPreferenceService.get_preferences(user_id)
        preference_list = generate_preferences_template(user_preferences)

        try:
            if url:
                recipes = await cls._scrape_recipes(url)
                print(recipes)
                recipe = cls._get_unique_recipe(recipes, set(), user_preferences, "", preference_list,
                                                user_description, True)
                recipe = AIGenerateMealPlan._prepare_for_mongodb(recipe.dict())
                recipe = await recipes_collection.insert_one(recipe)
                return recipe
            else:
                recipe = await cls._generate_unique_recipe(MealType.Empty, preference_list, None, user_description, True)
                recipe_dict = AIGenerateMealPlan._prepare_for_mongodb(recipe.dict())
                await recipes_collection.insert_one(recipe_dict)
                return recipe_dict

        except Exception as e:
            return {"error": str(e)}

    @classmethod
    async def regenerate_recipe(cls, user_id: str, recipe_id: str,
                                meal_plan_id: Optional[str]) -> RecipeCreate:
        """
        Regenerate a single recipe within a meal plan.

        Args:
            user_id: ID of the user
            meal_plan_id: ID of the meal plan
            recipe_id: ID of the recipe to regenerate

        Returns:
            The regenerated recipe

        Raises:
            HTTPException: If meal plan or recipe is not found
            :param meal_plan_id:
            :param user_id:
            :param recipe_id:
            :param meal_type:
        """
        user_preferences = await UserPreferenceService.get_preferences(user_id)
        preference_list = generate_preferences_template(user_preferences)

        # Regenerate the recipe
        regenerated_recipe = await cls._generate_unique_recipe("", preference_list, None, "", True)

        # return regenerated_recipe

        if meal_plan_id:
            try:
                # Fetch the meal plan using meal_id
                meal_plan = await meal_plans_collection.find_one({
                    "user_id": user_id,
                    "meal_id": meal_plan_id
                })

                if not meal_plan:
                    raise HTTPException()

                # Search for the recipe in the meal plan
                recipe_found = False
                recipe_id = ObjectId(recipe_id)
                for day in meal_plan.get("days", []):
                    for recipe in day.get("recipes", []):
                        if recipe.get("id") == recipe_id:
                            # Update the recipe and mark it as found
                            recipe.update(regenerated_recipe)
                            recipe["id"] = recipe_id
                            recipe["date_updated"] = datetime.now()
                            recipe_found = True
                            break
                    if recipe_found:
                        break

                if not recipe_found:
                    raise HTTPException()

                # Update the updated_at timestamp for the meal plan
                meal_plan["updated_at"] = datetime.now()

                meal_plan = AIGenerateMealPlan._prepare_for_mongodb(meal_plan)

                # Replace the entire meal plan document in the database
                await meal_plans_collection.replace_one(
                    {"user_id": user_id, "meal_id": meal_plan_id},
                    meal_plan
                )

                # Return the updated meal plan
                return meal_plan

            except Exception as e:
                raise HTTPException(e)
        else:
            recipe_to_save = AIGenerateMealPlan._prepare_for_mongodb(regenerated_recipe.dict())
            rec_id = ObjectId(recipe_id)

            recipe_db = await recipes_collection.find_one({
                "id": rec_id
            })

            if not recipe_db:
                raise HTTPException()

            # Search for the recipe in the meal plan
            recipe_found = False
            if recipe_db.get("id") == rec_id:
                # Update the recipe and mark it as found
                recipe_db.update(recipe_to_save)
                recipe_db["id"] = rec_id
                recipe_db["date_updated"] = datetime.now()
                recipe_found = True

            if not recipe_found:
                raise HTTPException()

            # Update the updated_at timestamp for the meal plan
            recipe_db["updated_at"] = datetime.now()

            await recipes_collection.replace_one(
                {"id": rec_id},
                recipe_db)
            return recipe_db
