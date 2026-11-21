
from collections import defaultdict
from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from app.repositories import report_repository

router = APIRouter(prefix="/api/reports", tags=["Manager Reports"])


def _period(start_date: date, end_date: date):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Invalid time range")

    return (
        datetime.combine(start_date, time.min),
        datetime.combine(end_date, time.max),
    )


def _minutes(value: float | None) -> str:
    return "—" if value is None else f"{round(value)} mins"


def _is_completed_delivery(delivery) -> bool:
    """
    A delivery is completed when the delivery outcome is DELIVERED
    and the completion timestamp exists.

    pickup_at is intentionally NOT required because this project
    does not implement a real shipper/pickup workflow.
    """
    return (
        delivery.outcome == "DELIVERED"
        and delivery.delivered_at is not None
    )


@router.get("/sales")
def get_sales_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    start_dt, end_dt = _period(start_date, end_date)

    orders = report_repository.get_orders_in_range(db, start_dt, end_dt)
    deliveries = report_repository.get_deliveries_by_order_range(
        db, start_dt, end_dt
    )

    avg_delivery = report_repository.average_delivery_minutes(deliveries)

    # Existing project rule: only DELIVERED orders contribute to revenue.
    revenue = sum(
        order.total for order in orders
        if order.status == "DELIVERED"
    )

    daily = defaultdict(lambda: {"orders": 0, "revenue": 0})

    for order in orders:
        day = order.created_at.date()
        daily[day]["orders"] += 1

        if order.status == "DELIVERED":
            daily[day]["revenue"] += order.total

    rows = []

    for day, values in sorted(daily.items()):
        day_deliveries = [
            delivery for delivery in deliveries
            if delivery.delivered_at
            and delivery.delivered_at.date() == day
        ]

        rows.append({
            "label": day.strftime("%d"),
            "date": day.strftime("%d %b %Y"),
            "orders": values["orders"],
            "revenue": values["revenue"],
            "chartVal": values["revenue"] / 1_000_000,
            "delivery": _minutes(
                report_repository.average_delivery_minutes(day_deliveries)
            ),
        })

    return {
        "kpis": [
            {"label": "Total Revenue", "value": f"{revenue:,} VND"},
            {"label": "Total Orders", "value": f"{len(orders):,}"},
            {"label": "Avg. Delivery Time", "value": _minutes(avg_delivery)},
        ],
        "totalSummary": f"Total: {revenue:,} VND · {len(orders):,} orders",
        "rows": rows,
    }


@router.get("/hub-workload")
def get_hub_workload_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    start_dt, end_dt = _period(start_date, end_date)

    hubs = report_repository.get_all_hubs(db)
    history = report_repository.get_status_history_in_range(
        db, start_dt, end_dt
    )

    history_order_ids = {entry.order_id for entry in history}

    total_orders = 0
    completed_orders = 0
    hubs_with_orders = 0
    rows = []

    for hub in hubs:
        orders = report_repository.get_hub_orders_in_range(
            db, hub.hub_id, start_dt, end_dt
        )

        total = len(orders)
        completed = sum(
            1 for order in orders
            if order.status == "DELIVERED"
        )
        not_delivered = total - completed

        total_orders += total
        completed_orders += completed

        if total > 0:
            hubs_with_orders += 1

            rows.append({
                "label": f"Hub {hub.hub_id}",
                "col1": hub.name,
                "col2": f"{total:,}",
                "col3": f"{completed:,}",
                "col4": f"{not_delivered:,}",
                "chartVal": total,
            })

    return {
        "kpis": [
            {"label": "Total Hub Orders", "value": f"{total_orders:,}"},
            {"label": "Completed Orders", "value": f"{completed_orders:,}"},
            {"label": "Hubs with Orders", "value": f"{hubs_with_orders:,}"},
        ],
        "totalSummary": f"Total: {total_orders:,} orders",
        "rows": rows,
        "statusHistoryRecords": len(history_order_ids),
    }


@router.get("/delivery")
def get_delivery_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    start_dt, end_dt = _period(start_date, end_date)

    deliveries = report_repository.get_deliveries_by_order_range(
        db, start_dt, end_dt
    )

    # Completion does not depend on pickup_at.
    # Admin's demo action records DELIVERED + delivered_at.
    completed = [
        delivery for delivery in deliveries
        if _is_completed_delivery(delivery)
    ]

    # Duration is only measurable when both timestamps are valid.
    avg_delivery = report_repository.average_delivery_minutes(completed)

    daily = defaultdict(list)

    for delivery in deliveries:
        # Report period is based on order creation date.
        daily[delivery.order.created_at.date()].append(delivery)

    rows = []

    for day, day_deliveries in sorted(daily.items()):
        day_completed = [
            delivery for delivery in day_deliveries
            if _is_completed_delivery(delivery)
        ]

        rows.append({
            "label": day.strftime("%d"),
            "col1": day.strftime("%d %b %Y"),
            "col2": str(len(day_deliveries)),
            "col3": _minutes(
                report_repository.average_delivery_minutes(day_completed)
            ),
            "chartVal": len(day_completed),
        })

    return {
        "kpis": [
            {"label": "Total Deliveries", "value": f"{len(deliveries):,}"},
            {"label": "Completed Deliveries", "value": f"{len(completed):,}"},
            {"label": "Avg. Delivery Time", "value": _minutes(avg_delivery)},
        ],
        "totalSummary": (
            f"Total: {len(deliveries):,} deliveries · "
            f"{len(completed):,} completed"
        ),
        "rows": rows,
    }
