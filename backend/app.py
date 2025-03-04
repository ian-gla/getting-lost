from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import position, user, event
import logging

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "level": "INFO", #"INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["default"],
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="getting-lost",
        description="Simple API to handle getting-lost app responses",
        version="1.0",
    )

    # TODO: update this in production

    origins = [
	"http://chekov.geog.gla.ac.uk/getting-lost/"
        "http://localhost:1234/",
        "http://127.0.0.1:1234/",
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
