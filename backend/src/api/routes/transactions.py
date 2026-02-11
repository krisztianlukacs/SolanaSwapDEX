import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user_wallet
from src.api.schemas.common import PaginationMeta
from src.api.schemas.transactions import TransactionResponse, TransactionListResponse
from src.common.constants import (
    lamports_to_sol,
    usdc_base_to_human,
    WSOL_MINT,
    SIGNAL_SOL_TO_USDC,
)
from src.db.repositories.transaction_repo import TransactionRepository

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _tx_to_response(tx) -> TransactionResponse:
    """Convert a Transaction model to response schema with human-readable amounts."""
    is_sol_to_usdc = tx.type == SIGNAL_SOL_TO_USDC
    amount_in = lamports_to_sol(tx.amount_in) if is_sol_to_usdc else usdc_base_to_human(tx.amount_in)
    amount_out = usdc_base_to_human(tx.amount_out) if is_sol_to_usdc else lamports_to_sol(tx.amount_out)
    fee = lamports_to_sol(tx.fee) if tx.token_in == WSOL_MINT else usdc_base_to_human(tx.fee)

    return TransactionResponse(
        id=tx.id,
        date=tx.date,
        type=tx.type,
        amount_in=round(amount_in, 9),
        amount_out=round(amount_out, 9),
        token_in=tx.token_in,
        token_out=tx.token_out,
        slippage_bps=tx.slippage_bps,
        fee=round(fee, 9),
        status=tx.status,
        signature=tx.signature,
        error_message=tx.error_message,
    )


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
    type: str | None = Query(None, description="Filter by type: SOL_TO_USDC or USDC_TO_SOL"),
    status: str | None = Query(None, description="Filter by status: confirmed, pending, failed"),
    date_from: datetime | None = Query(None, description="Filter from date"),
    date_to: datetime | None = Query(None, description="Filter to date"),
    sort_by: str = Query("date", description="Sort field"),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> TransactionListResponse:
    tx_repo = TransactionRepository(db)

    transactions, total = await tx_repo.list_for_owner(
        wallet,
        type_filter=type,
        status_filter=status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )

    total_pages = (total + page_size - 1) // page_size

    return TransactionListResponse(
        transactions=[_tx_to_response(tx) for tx in transactions],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/export")
async def export_transactions_csv(
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
    type: str | None = Query(None),
    status: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
) -> StreamingResponse:
    tx_repo = TransactionRepository(db)

    transactions, _ = await tx_repo.list_for_owner(
        wallet,
        type_filter=type,
        status_filter=status,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10000,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Type", "Amount In", "Amount Out", "Slippage BPS", "Fee", "Status", "Signature"])

    for tx in transactions:
        resp = _tx_to_response(tx)
        writer.writerow([
            resp.date.isoformat(),
            resp.type,
            resp.amount_in,
            resp.amount_out,
            resp.slippage_bps,
            resp.fee,
            resp.status,
            resp.signature or "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )
