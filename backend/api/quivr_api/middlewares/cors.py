import os

from fastapi.middleware.cors import CORSMiddleware


def get_allowed_origins():
    """
    Get allowed CORS origins from environment variables.
    Only allows requests from configured frontend and Moodle instances.
    """
    origins = []

    # Frontend URL (required for the React app)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    if frontend_url:
        origins.append(frontend_url)
        # Also add without trailing slash if present
        if frontend_url.endswith("/"):
            origins.append(frontend_url.rstrip("/"))

    # Moodle URL (required for Moodle plugin integration)
    moodle_url = os.getenv("MOODLE_URL")
    if moodle_url:
        origins.append(moodle_url)
        # Also add without trailing slash if present
        if moodle_url.endswith("/"):
            origins.append(moodle_url.rstrip("/"))

    # Development: allow localhost variants
    if os.getenv("ENVIRONMENT", "development").lower() in ["development", "dev", "local"]:
        dev_origins = [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
        ]
        for origin in dev_origins:
            if origin not in origins:
                origins.append(origin)

    return origins


def add_cors_middleware(app):
    allowed_origins = get_allowed_origins()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
