from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Voucher


def expire_vouchers(db: Session, now: datetime | None = None) -> int:
    """Apply the UC05 ACTIVE -> EXPIRED transition when current time exceeds end_date."""
    now = now or datetime.now()
    changed = (
        db.query(Voucher)
        .filter(Voucher.status == "ACTIVE", Voucher.end_date < now)
        .update({Voucher.status: "EXPIRED"}, synchronize_session="fetch")
    )
    if changed:
        db.commit()
    return int(changed)


def get_vouchers(
    db: Session,
    status_filter: str | None = None,
    search: str | None = None,
) -> list[Voucher]:
    expire_vouchers(db)
    query = db.query(Voucher)
    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(Voucher.status == status_filter.strip().upper())
    if search and search.strip():
        query = query.filter(Voucher.code.ilike(f"%{search.strip()}%"))
    return query.order_by(Voucher.voucher_id.desc()).all()


def get_voucher_by_code(db: Session, code: str) -> Voucher | None:
    expire_vouchers(db)
    return db.query(Voucher).filter(Voucher.code == code).first()


def get_voucher_by_id(db: Session, voucher_id: int) -> Voucher | None:
    expire_vouchers(db)
    return db.query(Voucher).filter(Voucher.voucher_id == voucher_id).first()


def create_voucher(
    db: Session, code: str, discount_type: str, discount_value: int,
    min_order: int, start_date: datetime, end_date: datetime,
) -> Voucher:
    voucher = Voucher(
        code=code, discount_type=discount_type, discount_value=discount_value,
        min_order=min_order, start_date=start_date, end_date=end_date,
        status="ACTIVE",
    )
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    expire_vouchers(db)
    db.refresh(voucher)
    return voucher


def update_voucher(
    db: Session, voucher: Voucher, *, code: str, discount_type: str,
    discount_value: int, min_order: int, start_date: datetime, end_date: datetime,
) -> Voucher:
    voucher.code = code
    voucher.discount_type = discount_type
    voucher.discount_value = discount_value
    voucher.min_order = min_order
    voucher.start_date = start_date
    voucher.end_date = end_date
    db.commit()
    db.refresh(voucher)
    expire_vouchers(db)
    db.refresh(voucher)
    return voucher


def archive_voucher(db: Session, voucher: Voucher) -> Voucher:
    if voucher.status not in {"ACTIVE", "EXPIRED"}:
        raise ValueError("Only ACTIVE or EXPIRED vouchers can be archived.")
    voucher.status = "ARCHIVED"
    db.commit()
    db.refresh(voucher)
    return voucher
