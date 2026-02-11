from fastapi import APIRouter

from .health import router as health_router
from .portfolio import router as portfolio_router
from .vaults import router as vaults_router
from .strategy import router as strategy_router
from .transactions import router as transactions_router
from .pnl import router as pnl_router
from .settings import router as settings_router
from .signals import router as signals_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(portfolio_router)
api_router.include_router(vaults_router)
api_router.include_router(strategy_router)
api_router.include_router(transactions_router)
api_router.include_router(pnl_router)
api_router.include_router(settings_router)
api_router.include_router(signals_router)
