import logging

from fastapi import FastAPI

from app.config import get_settings
from app.middleware import setup_middleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="B2B platform for Egypt's fiber optic sector",
        version="0.1.0",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    setup_middleware(app)
    _register_routers(app, settings.api_prefix)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": settings.app_name}

    return app


def _register_routers(app: FastAPI, prefix: str) -> None:
    from app.auth.router import router as auth_router
    from app.users.router import router as users_router
    from app.companies.router import router as companies_router
    from app.categories.router import router as categories_router
    from app.profiles.router import router as profiles_router
    from app.rfqs.router import router as rfqs_router
    from app.messages.router import router as messages_router
    from app.verification.router import router as verification_router
    from app.search.router import router as search_router
    from app.storage.router import router as upload_router
    from app.notifications.router import router as notifications_router
    from app.reviews.router import router as reviews_router
    from app.admin.router import router as admin_router

    app.include_router(auth_router, prefix=f"{prefix}/auth", tags=["Auth"])
    app.include_router(users_router, prefix=f"{prefix}/users", tags=["Users"])
    app.include_router(companies_router, prefix=f"{prefix}/companies", tags=["Companies"])
    app.include_router(categories_router, prefix=f"{prefix}/categories", tags=["Categories"])
    app.include_router(profiles_router, prefix=f"{prefix}/profiles", tags=["Profiles"])
    app.include_router(rfqs_router, prefix=f"{prefix}/rfqs", tags=["RFQs"])
    app.include_router(messages_router, prefix=f"{prefix}/messages", tags=["Messages"])
    app.include_router(verification_router, prefix=f"{prefix}/verification", tags=["Verification"])
    app.include_router(search_router, prefix=f"{prefix}/search", tags=["Search"])
    app.include_router(upload_router, prefix=f"{prefix}/upload", tags=["Upload"])
    app.include_router(notifications_router, prefix=f"{prefix}/notifications", tags=["Notifications"])
    app.include_router(reviews_router, prefix=f"{prefix}/reviews", tags=["Reviews"])
    app.include_router(admin_router, prefix=f"{prefix}/admin", tags=["Admin"])


app = create_app()
