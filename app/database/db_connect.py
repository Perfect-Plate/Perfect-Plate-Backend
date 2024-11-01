import logging
from typing import Annotated
from dotenv import load_dotenv
import os
from fastapi import Depends, HTTPException
from supabase import create_client, Client

from app.models.dietarypreferences import DietaryPreferences

# Load environment variables from .env file
load_dotenv()

# Create Supabase client using environment variables
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

print(f"Supabase URL: {url}, Key: {key}")  # Debugging line

if not url or not key:
    logging.error("Supabase URL or Key not found in environment variables.")
    raise ValueError("Supabase URL and Key must be set in the environment variables.")

# Create the Supabase client
client: Client = create_client(url, key)

#
# async def get_db() -> Client:
#     """Get a Supabase client without user authentication."""
#     try:
#         # Check if the connection is successful
#         response = client.table("users").select("*").execute()
#         if not response:  # Change this line to access the data attribute
#             raise HTTPException(status_code=500, detail="Database connection failed")
#         return client  # Return the client directly
#
#     except Exception as e:
#         logging.error(f"Database connection error: {e}")
#         raise HTTPException(status_code=500, detail="Database connection error")
#
#
# SessionDep = Annotated[Client, Depends(get_db)]
