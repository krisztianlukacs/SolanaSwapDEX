from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str


class ErrorResponse(BaseModel):
    error: str


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
