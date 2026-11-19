from datetime import datetime

from fastapi import HTTPException


def calculate_voucher_discount(voucher, subtotal: int) -> int:
    if voucher is None:
        raise HTTPException(status_code=400, detail="Voucher code was not found. Check the code and try again.")
    if voucher.status == "ARCHIVED":
        raise HTTPException(status_code=400, detail="This voucher has been archived.")

    now = datetime.now()
    if voucher.start_date > now:
        raise HTTPException(status_code=400, detail="This voucher is not valid yet.")
    if voucher.end_date < now or voucher.status == "EXPIRED":
        raise HTTPException(status_code=400, detail="This voucher has expired.")
    if voucher.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="This voucher is not active.")
    if subtotal < voucher.min_order:
        remaining = voucher.min_order - subtotal
        raise HTTPException(
            status_code=400,
            detail=(f"Minimum order for this voucher is {voucher.min_order:,} VND. "
                    f"Add {remaining:,} VND more to apply it."),
        )

    discount = (subtotal * voucher.discount_value // 100
                if voucher.discount_type == "PERCENT" else voucher.discount_value)
    return min(discount, subtotal)
