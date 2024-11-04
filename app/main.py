import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.routes import api_router
from app.utils.core.settings import settings
from app.utils.core.events import lifespan


# Create the FastAPI application
def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=lambda router: f"{router.tags[0]}-{router.name}",
    )

    # Set CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include API routes
    from app.routers.routes import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=5000)