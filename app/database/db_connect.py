import logging
from typing import Annotated
from dotenv import load_dotenv
import os

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from gotrue.errors import AuthApiError
from httpx import AsyncClient
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

from app.schemas.auth import UserIn

from app.models.dietarypreferences import DietaryPreferences

# Load environment variables from .env file
load_dotenv()

# Create Supabase client using environment variables
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


if not url or not key:
    logging.error("Supabase URL or Key not found in environment variables.")
    raise ValueError("Supabase URL and Key must be set in the environment variables.")

super_client: AsyncClient | None = None


async def init_super_client() -> None:
    """for validation access_token init at life span event"""
    global super_client
    super_client = create_client(
        url,
        key,
        options=ClientOptions(postgrest_client_timeout=10, storage_client_timeout=10) or None,
    )
    # await super_client.auth.sign_in_with_password(
    #     {"email": settings.SUPERUSER_EMAIL, "password": settings.SUPERUSER_PASSWORD}
    # )


# auto get access_token from header
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="https://api.perfectplate.com/auth/v1/token"
)
AccessTokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(access_token: AccessTokenDep) -> UserIn:
    """get current user from access_token and  validate same time"""
    if not super_client:
        raise HTTPException(status_code=500, detail="Super client not initialized")

    user_rsp = await super_client.auth.get_user(jwt=access_token)
    if not user_rsp:
        logging.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    return UserIn(**user_rsp.user.model_dump(), access_token=access_token)


CurrentUser = Annotated[UserIn, Depends(get_current_user)]


async def get_current_user(access_token: AccessTokenDep) -> UserIn:
    """Get current user from access_token and validate at the same time."""
    user_rsp = await super_client.auth.get_user(jwt=access_token)
    if not user_rsp:
        logging.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    return UserIn(**user_rsp.user.model_dump(), access_token=access_token)


CurrentUser = Annotated[UserIn, Depends(get_current_user)]


async def get_db(user: CurrentUser) -> AsyncClient:
    client: AsyncClient | None = None
    try:
        client = await create_client(
            url, key,
            options=ClientOptions(
                postgrest_client_timeout=30,
                storage_client_timeout=30,
                headers={"Authorization": f"Bearer {user.access_token}"},
            ) or None,
        )

        # Check if the connection is successful
        response = await client.table("perfect_plate").select("*").execute()
        if response[0] is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        yield client

    except AuthApiError as e:
        logging.error(e)
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


SessionDep = Annotated[AsyncClient, Depends(get_db)]
