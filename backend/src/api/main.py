from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.middleware.cors import add_cors_middleware
from src.api.middleware.error_handler import add_error_handlers
from src.api.middleware.request_logging import RequestLoggingMiddleware
from src.api.routes import api_router
from src.common.logging import setup_logger
from src.db.base import engine

logger = setup_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SolanaSwapDEX API")
    yield
    logger.info("Shutting down SolanaSwapDEX API")
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SolanaSwapDEX API",
        description="Backend API for SOL/USDC strategy execution",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Middleware (order matters — last added runs first)
    add_cors_middleware(app)
    app.add_middleware(RequestLoggingMiddleware)

    # Error handlers
    add_error_handlers(app)

    # Routes
    app.include_router(api_router)

    return app


app = create_app()
