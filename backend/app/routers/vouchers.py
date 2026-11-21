import re
from datetime import date, datetime, time
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Voucher
from app.repositories import voucher_repository

router = APIRouter(prefix="/api/vouchers", tags=["Admin Vouchers"])
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _format_display_date(value: date) -> str:
    return f"{value.day:02d} {MONTH_NAMES[value.month - 1]} {value.year}"


def _parse_discount_input(raw: str) -> tuple[str, int]:
    cleaned = raw.strip().upper()
    if cleaned.endswith("%"):
        number = cleaned[:-1].strip()
        if not number.isdigit() or not 1 <= int(number) <= 100:
            raise HTTPException(400, "Percentage discount must be between 1% and 100%.")
        return "PERCENT", int(number)
    digits = re.sub(r"[^\\d]", "", cleaned)
    if not digits or int(digits) <= 0:
        raise HTTPException(400, "Invalid discount value. Use e.g. '20%' or '30000'.")
    return "FIXED", int(digits)


class VoucherWrite(BaseModel):
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
    start_date: str
    end_date: str


def _to_voucher_out(voucher: Voucher) -> dict:
    discount = (f"{voucher.discount_value}%" if voucher.discount_type == "PERCENT"
                else f"{voucher.discount_value:,} VND")
    return {
        "id": voucher.voucher_id,
        "code": voucher.code,
        "hub": "All hubs",
        "discount": discount,
        "min_order": f"{voucher.min_order:,} VND",
        "valid_from": _format_display_date(voucher.start_date.date()),
        "valid_to": _format_display_date(voucher.end_date.date()),
        "status": voucher.status,
        "start_date": voucher.start_date.date().isoformat(),
        "end_date": voucher.end_date.date().isoformat(),
    }


def _validated_payload(payload: VoucherWrite):
    code = payload.code.strip().upper()
    if not code:
        raise HTTPException(400, "Voucher code is required.")
    if payload.end_date < payload.start_date:
        raise HTTPException(400, "Invalid time range")
    discount_type, discount_value = _parse_discount_input(payload.discount)
    return code, discount_type, discount_value


@router.get("", response_model=list[VoucherOut])
def list_vouchers(
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    rows = voucher_repository.get_vouchers(db, status_filter, search)
    return [_to_voucher_out(row) for row in rows]


@router.post("", response_model=VoucherOut, status_code=status.HTTP_201_CREATED)
def create_voucher(payload: VoucherWrite, db: Session = Depends(get_db)):
    code, discount_type, discount_value = _validated_payload(payload)
    if voucher_repository.get_voucher_by_code(db, code):
        raise HTTPException(409, f"Voucher code '{code}' already exists.")
    voucher = voucher_repository.create_voucher(
        db, code, discount_type, discount_value, payload.min_order,
        datetime.combine(payload.start_date, time.min),
        datetime.combine(payload.end_date, time.max),
    )
    return _to_voucher_out(voucher)


@router.put("/{voucher_id}", response_model=VoucherOut)
def update_voucher(voucher_id: int, payload: VoucherWrite, db: Session = Depends(get_db)):
    voucher = voucher_repository.get_voucher_by_id(db, voucher_id)
    if voucher is None:
        raise HTTPException(404, "Voucher not found.")
    if voucher.status == "ARCHIVED":
        raise HTTPException(409, "ARCHIVED vouchers cannot be updated.")
    code, discount_type, discount_value = _validated_payload(payload)
    duplicate = voucher_repository.get_voucher_by_code(db, code)
    if duplicate is not None and duplicate.voucher_id != voucher_id:
        raise HTTPException(409, f"Voucher code '{code}' already exists.")
    updated = voucher_repository.update_voucher(
        db, voucher, code=code, discount_type=discount_type,
        discount_value=discount_value, min_order=payload.min_order,
        start_date=datetime.combine(payload.start_date, time.min),
        end_date=datetime.combine(payload.end_date, time.max),
    )
    return _to_voucher_out(updated)


@router.patch("/{voucher_id}/archive", response_model=VoucherOut)
def archive_voucher(voucher_id: int, db: Session = Depends(get_db)):
    voucher = voucher_repository.get_voucher_by_id(db, voucher_id)
    if voucher is None:
        raise HTTPException(404, "Voucher not found.")
    if voucher.status not in {"ACTIVE", "EXPIRED"}:
        raise HTTPException(409, "Only ACTIVE or EXPIRED vouchers can be archived.")
    return _to_voucher_out(voucher_repository.archive_voucher(db, voucher))
