from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Voucher


def get_vouchers(
    db: Session,
    status_filter: str | None = None,
    search: str | None = None,
) -> list[Voucher]:
    query = db.query(Voucher)

    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(Voucher.status == status_filter.strip().upper())

    if search and search.strip():
        kw = f"%{search.strip()}%"
        query = query.filter(Voucher.code.ilike(kw))

    return query.order_by(Voucher.voucher_id.desc()).all()


def get_voucher_by_code(db: Session, code: str) -> Voucher | None:
    return db.query(Voucher).filter(Voucher.code == code).first()


def get_voucher_by_id(db: Session, voucher_id: int) -> Voucher | None:
    return db.query(Voucher).filter(Voucher.voucher_id == voucher_id).first()


def create_voucher(
    db: Session,
    code: str,
    discount_type: str,
    discount_value: int,
    min_order: int,
    start_date: datetime,
    end_date: datetime,
) -> Voucher:
    new_voucher = Voucher(
        code=code,
        discount_type=discount_type,
        discount_value=discount_value,
        min_order=min_order,
        start_date=start_date,
        end_date=end_date,
        status="ACTIVE",
    )
    db.add(new_voucher)
    db.commit()
    db.refresh(new_voucher)
    return new_voucher


def archive_voucher(db: Session, voucher: Voucher) -> Voucher:
    voucher.status = "ARCHIVED"
    db.commit()
    db.refresh(voucher)
    return voucher