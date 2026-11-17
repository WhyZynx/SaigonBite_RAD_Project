import re
from datetime import date, datetime, time
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Voucher
from app.repositories import voucher_repository

router = APIRouter(prefix="/api/vouchers", tags=["Admin Vouchers"])

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _format_display_date(d: date) -> str:
    return f"{d.day:02d} {MONTH_NAMES[d.month - 1]} {d.year}"


def _parse_discount_input(raw: str) -> tuple[str, int]:
    cleaned = raw.strip().upper()
    if cleaned.endswith("%"):
        num_str = cleaned[:-1].strip()
        if not num_str.isdigit() or not (1 <= int(num_str) <= 100):
            raise HTTPException(status_code=400, detail="Percentage discount must be between 1% and 100%.")
        return "PERCENT", int(num_str)
    digits = re.sub(r"[^\d]", "", cleaned)
    if not digits or int(digits) <= 0:
        raise HTTPException(status_code=400, detail="Invalid discount value. Use e.g. '20%' or '30000'.")
    return "FIXED", int(digits)


class VoucherCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=32)
    hub: str = Field(default="All hubs", max_length=64)
    discount: str = Field(..., min_length=1, max_length=32)
    min_order: int = Field(..., ge=0)
    start_date: date
    end_date: date


class VoucherOut(BaseModel):
    id: int
    code: str
    hub: str
    discount: str
    min_order: str
    valid_from: str
    valid_to: str
    status: str


def _to_voucher_out(v: Voucher, hub_label: str = "All hubs") -> dict:
    discount_str = f"{v.discount_value}%" if v.discount_type == "PERCENT" else f"{v.discount_value:,} VND"
    return {
        "id": v.voucher_id,
        "code": v.code,
        "hub": hub_label,
        "discount": discount_str,
        "min_order": f"{v.min_order:,} VND",
        "valid_from": f"{_format_display_date(v.start_date.date())} –",
        "valid_to": _format_display_date(v.end_date.date()),
        "status": v.status,
    }


@router.get("", response_model=list[VoucherOut])
def list_vouchers(
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    vouchers = voucher_repository.get_vouchers(db, status_filter=status_filter, search=search)
    return [_to_voucher_out(v) for v in vouchers]


@router.post("", response_model=VoucherOut, status_code=status.HTTP_201_CREATED)
def create_voucher(payload: VoucherCreate, db: Session = Depends(get_db)):
    normalized_code = payload.code.strip().upper()
    if not normalized_code:
        raise HTTPException(status_code=400, detail="Voucher code is required.")

    if payload.end_date < payload.start_date:
        raise HTTPException(
            status_code=400,
            detail="Valid until date cannot be earlier than valid from date.",
        )

    if voucher_repository.get_voucher_by_code(db, normalized_code):
        raise HTTPException(
            status_code=409,
            detail=f"Voucher code '{normalized_code}' already exists.",
        )

    discount_type, discount_value = _parse_discount_input(payload.discount)

    new_voucher = voucher_repository.create_voucher(
        db=db,
        code=normalized_code,
        discount_type=discount_type,
        discount_value=discount_value,
        min_order=payload.min_order,
        start_date=datetime.combine(payload.start_date, time.min),
        end_date=datetime.combine(payload.end_date, time(23, 59, 59)),
    )

    return _to_voucher_out(new_voucher, hub_label=payload.hub.strip() or "All hubs")


@router.patch("/{voucher_id}/archive", response_model=VoucherOut)
def archive_voucher(voucher_id: int, db: Session = Depends(get_db)):
    voucher = voucher_repository.get_voucher_by_id(db, voucher_id)
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found.")

    if voucher.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Only ACTIVE vouchers can be archived.",
        )

    updated_voucher = voucher_repository.archive_voucher(db, voucher)
    return _to_voucher_out(updated_voucher)