from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Voucher

router = APIRouter(prefix="/api/vouchers", tags=["Admin Vouchers"])

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _format_display_date(d: date) -> str:
    return f"{d.day:02d} {MONTH_NAMES[d.month - 1]} {d.year}"


class VoucherCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=32)
    hub: str = Field(default="All hubs", max_length=64)
    discount_type: str = Field(..., pattern="^(PERCENT|FIXED)$")
    discount_value: int = Field(..., gt=0)
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

    class Config:
        from_attributes = True


@router.get("", response_model=list[VoucherOut])
def list_vouchers(
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Voucher)

    if status_filter and status_filter.upper() != "ALL":
        target_status = status_filter.strip().upper()
        query = query.filter(Voucher.status == target_status)

    if search and search.strip():
        kw = f"%{search.strip().lower()}%"
        query = query.filter(Voucher.code.ilike(kw))

    vouchers = query.all()
    results = []
    for v in vouchers:
        discount_str = f"{v.discount_value}%" if v.discount_type == "PERCENT" else f"{v.discount_value:,} VND"
        results.append({
            "id": v.voucher_id,
            "code": v.code,
            "hub": "All hubs",
            "discount": discount_str,
            "min_order": f"{v.min_order:,} VND",
            "valid_from": f"{_format_display_date(v.start_date.date())} –" if v.start_date else "",
            "valid_to": _format_display_date(v.end_date.date()) if v.end_date else "",
            "status": v.status,
        })

    return results


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

    existing = db.query(Voucher).filter(Voucher.code == normalized_code).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Voucher code '{normalized_code}' already exists.",
        )

    new_voucher = Voucher(
        code=normalized_code,
        discount_type=payload.discount_type,
        discount_value=payload.discount_value,
        min_order=payload.min_order,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status="ACTIVE",
    )
    db.add(new_voucher)
    db.commit()
    db.refresh(new_voucher)

    discount_str = f"{new_voucher.discount_value}%" if new_voucher.discount_type == "PERCENT" else f"{new_voucher.discount_value:,} VND"
    return {
        "id": new_voucher.voucher_id,
        "code": new_voucher.code,
        "hub": payload.hub.strip() or "All hubs",
        "discount": discount_str,
        "min_order": f"{new_voucher.min_order:,} VND",
        "valid_from": f"{_format_display_date(new_voucher.start_date.date())} –",
        "valid_to": _format_display_date(new_voucher.end_date.date()),
        "status": new_voucher.status,
    }


@router.patch("/{voucher_id}/archive", response_model=VoucherOut)
def archive_voucher(voucher_id: int, db: Session = Depends(get_db)):
    voucher = db.query(Voucher).filter(Voucher.voucher_id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found.")

    if voucher.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Only ACTIVE vouchers can be archived.",
        )

    voucher.status = "ARCHIVED"
    db.commit()
    db.refresh(voucher)

    discount_str = f"{voucher.discount_value}%" if voucher.discount_type == "PERCENT" else f"{voucher.discount_value:,} VND"
    return {
        "id": voucher.voucher_id,
        "code": voucher.code,
        "hub": "All hubs",
        "discount": discount_str,
        "min_order": f"{voucher.min_order:,} VND",
        "valid_from": f"{_format_display_date(voucher.start_date.date())} –" if voucher.start_date else "",
        "valid_to": _format_display_date(voucher.end_date.date()) if voucher.end_date else "",
        "status": voucher.status,
    }