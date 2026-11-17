from datetime import date
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

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


_VOUCHERS_STORE: list[dict] = [
    {
        "id": 1,
        "code": "BITEWELCOME",
        "hub": "All hubs",
        "discount": "20%",
        "min_order": "150,000 VND",
        "valid_from": "01 Nov 2026 –",
        "valid_to": "31 Dec 2026",
        "status": "ACTIVE",
    },
    {
        "id": 2,
        "code": "SAIGON50K",
        "hub": "All hubs",
        "discount": "50,000 VND",
        "min_order": "250,000 VND",
        "valid_from": "01 Nov 2026 –",
        "valid_to": "30 Nov 2026",
        "status": "ACTIVE",
    },
    {
        "id": 3,
        "code": "FREESHIPD1",
        "hub": "Bite Hub D1",
        "discount": "25,000 VND",
        "min_order": "100,000 VND",
        "valid_from": "10 Nov 2026 –",
        "valid_to": "30 Nov 2026",
        "status": "ACTIVE",
    },
    {
        "id": 4,
        "code": "D7LUNCH",
        "hub": "Bite Hub D7",
        "discount": "15%",
        "min_order": "120,000 VND",
        "valid_from": "01 Nov 2026 –",
        "valid_to": "30 Nov 2026",
        "status": "ACTIVE",
    },
    {
        "id": 5,
        "code": "THUDUC30",
        "hub": "Bite Hub Thu Duc",
        "discount": "30,000 VND",
        "min_order": "180,000 VND",
        "valid_from": "01 Nov 2026 –",
        "valid_to": "31 Dec 2026",
        "status": "ACTIVE",
    },
    {
        "id": 6,
        "code": "TET2026",
        "hub": "All hubs",
        "discount": "50,000 VND",
        "min_order": "200,000 VND",
        "valid_from": "01 Feb 2026 –",
        "valid_to": "28 Feb 2026",
        "status": "EXPIRED",
    },
    {
        "id": 7,
        "code": "SUMMERBITE",
        "hub": "All hubs",
        "discount": "10%",
        "min_order": "100,000 VND",
        "valid_from": "01 Jun 2026 –",
        "valid_to": "31 Aug 2026",
        "status": "ARCHIVED",
    },
    {
        "id": 8,
        "code": "D1WEEKEND",
        "hub": "Bite Hub D1",
        "discount": "20%",
        "min_order": "150,000 VND",
        "valid_from": "01 Aug 2026 –",
        "valid_to": "31 Aug 2026",
        "status": "ARCHIVED",
    },
]


@router.get("", response_model=list[VoucherOut])
def list_vouchers(
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
):
    results = _VOUCHERS_STORE
    if status_filter and status_filter.upper() != "ALL":
        target_status = status_filter.strip().upper()
        results = [v for v in results if v["status"] == target_status]

    if search and search.strip():
        kw = search.strip().lower()
        results = [
            v for v in results
            if kw in v["code"].lower() or kw in v["hub"].lower()
        ]

    return results


@router.post("", response_model=VoucherOut, status_code=status.HTTP_201_CREATED)
def create_voucher(payload: VoucherCreate):
    normalized_code = payload.code.strip().upper()
    if not normalized_code:
        raise HTTPException(status_code=400, detail="Voucher code is required.")

    if payload.end_date < payload.start_date:
        raise HTTPException(
            status_code=400,
            detail="Valid until date cannot be earlier than valid from date.",
        )

    if any(v["code"] == normalized_code for v in _VOUCHERS_STORE):
        raise HTTPException(
            status_code=409,
            detail=f"Voucher code '{normalized_code}' already exists.",
        )

    next_id = max((v["id"] for v in _VOUCHERS_STORE), default=0) + 1
    new_voucher = {
        "id": next_id,
        "code": normalized_code,
        "hub": payload.hub.strip() or "All hubs",
        "discount": payload.discount.strip(),
        "min_order": f"{payload.min_order:,} VND",
        "valid_from": f"{_format_display_date(payload.start_date)} –",
        "valid_to": _format_display_date(payload.end_date),
        "status": "ACTIVE",
    }
    _VOUCHERS_STORE.insert(0, new_voucher)
    return new_voucher


@router.patch("/{voucher_id}/archive", response_model=VoucherOut)
def archive_voucher(voucher_id: int):
    voucher = next((v for v in _VOUCHERS_STORE if v["id"] == voucher_id), None)
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found.")

    if voucher["status"] != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Only ACTIVE vouchers can be archived.",
        )

    voucher["status"] = "ARCHIVED"
    return voucher