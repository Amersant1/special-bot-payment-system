from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI(title="Payment Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from .routers import payments as payments_router  # noqa: E402
app.include_router(payments_router.router, prefix="/api/payments", tags=["payments"])


TORTOISE_CONFIG = {
    "connections": {"default": str(settings.DATABASE_URL)},
    "apps": {
        "models": {
            "models": [
                "app.models",  # our models package
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "UTC",
}

register_tortoise(
    app,
    config=TORTOISE_CONFIG,
    generate_schemas=False,
    add_exception_handlers=True,
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
