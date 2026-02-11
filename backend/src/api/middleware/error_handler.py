from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.common.exceptions import AppException
from src.common.logging import setup_logger

logger = setup_logger("api")


def add_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning("ERR %s | %d | %s", request_id, exc.status_code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception("ERR %s | 500 | %s", request_id, str(exc))
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
