from fastapi import APIRouter

openapi = APIRouter()


@openapi.get("/")
async def root():
    return {"message": "Ai related endpoints"}


@openapi.get("/prompt")
async def prompt():
    return {"message": "Prompt endpoint"}


@openapi.get("/swap")
async def complete():
    return {"message": "Complete endpoint"}
