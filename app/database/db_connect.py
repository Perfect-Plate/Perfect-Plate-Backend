import os

import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()


# MongoDB client setup
client = AsyncIOMotorClient(os.environ["MONGODB_URL"], tlsCAFile=certifi.where())
db = client.perfect_plates
users_collection = db.get_collection("users")
preferences_collection = db.get_collection("preferences")
meal_plans_collection = db.get_collection("meal_plans")
recipes_collection = db.get_collection("recipes")

# client = AsyncIOMotorClient(os.environ.get("MONGODB_URL"))
# db = client.perfect_plates
# users = db.users
# preferences = db.preferences
# meal_plans = db.meal_plans
# recipes = db.recipes
