from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import position, user, event


def create_app() -> FastAPI:
    app = FastAPI(
        title="getting-lost",
        description="Simple API to handle getting-lost app responses",
        version="1.0",
    )

    # TODO: update this in production

    origins = [
        "http://localhost:8000/",
        "http://127.0.0.1:8000/",
        "*",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(position.router)
    app.include_router(user.router)
    app.include_router(event.router)

    return app
