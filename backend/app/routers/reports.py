from datetime import date
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/reports", tags=["Manager Reports"])


def _validate_dates(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be earlier than start date.",
        )


@router.get("/sales")
def get_sales_report(
    start_date: date = Query(default=date(2026, 11, 1)),
    end_date: date = Query(default=date(2026, 11, 15)),
):
    _validate_dates(start_date, end_date)
    rows = [
        {"label": "01", "date": "01 Nov 2026", "orders": 192, "revenue": 24000000, "chartVal": 24.0, "delivery": "24 mins"},
        {"label": "02", "date": "02 Nov 2026", "orders": 208, "revenue": 26000000, "chartVal": 26.0, "delivery": "23 mins"},
        {"label": "03", "date": "03 Nov 2026", "orders": 224, "revenue": 28000000, "chartVal": 28.0, "delivery": "25 mins"},
        {"label": "04", "date": "04 Nov 2026", "orders": 240, "revenue": 30000000, "chartVal": 30.0, "delivery": "24 mins"},
        {"label": "05", "date": "05 Nov 2026", "orders": 280, "revenue": 35000000, "chartVal": 35.0, "delivery": "24 mins"},
        {"label": "06", "date": "06 Nov 2026", "orders": 336, "revenue": 42000000, "chartVal": 42.0, "delivery": "26 mins"},
        {"label": "07", "date": "07 Nov 2026", "orders": 304, "revenue": 38000000, "chartVal": 38.0, "delivery": "25 mins"},
        {"label": "08", "date": "08 Nov 2026", "orders": 176, "revenue": 22000000, "chartVal": 22.0, "delivery": "22 mins"},
        {"label": "09", "date": "09 Nov 2026", "orders": 200, "revenue": 25000000, "chartVal": 25.0, "delivery": "23 mins"},
        {"label": "10", "date": "10 Nov 2026", "orders": 216, "revenue": 27000000, "chartVal": 27.0, "delivery": "24 mins"},
        {"label": "11", "date": "11 Nov 2026", "orders": 232, "revenue": 29000000, "chartVal": 29.0, "delivery": "24 mins"},
        {"label": "12", "date": "12 Nov 2026", "orders": 248, "revenue": 31000000, "chartVal": 31.0, "delivery": "25 mins"},
        {"label": "13", "date": "13 Nov 2026", "orders": 208, "revenue": 26000000, "chartVal": 26.0, "delivery": "23 mins"},
        {"label": "14", "date": "14 Nov 2026", "orders": 192, "revenue": 24000000, "chartVal": 24.0, "delivery": "24 mins"},
        {"label": "15", "date": "15 Nov 2026", "orders": 164, "revenue": 21500000, "chartVal": 21.5, "delivery": "23 mins"},
    ]
    return {
        "kpis": [
            {"label": "Total Revenue", "value": "428,500,000 VND"},
            {"label": "Total Orders", "value": "3,420"},
            {"label": "Avg. Delivery Time", "value": "24 mins"},
        ],
        "totalSummary": "Total: 428,500,000 VND · 3,420 orders",
        "rows": rows,
    }


@router.get("/hub-workload")
def get_hub_workload_report(
    start_date: date = Query(default=date(2026, 11, 1)),
    end_date: date = Query(default=date(2026, 11, 15)),
):
    _validate_dates(start_date, end_date)
    return {
        "kpis": [
            {"label": "Total Hub Orders", "value": "3,420"},
            {"label": "Completed Orders", "value": "3,318"},
            {"label": "Avg. Prep Time", "value": "11 mins"},
        ],
        "totalSummary": "Total: 3,420 orders · 97.0% completion rate",
        "rows": [
            {"label": "D1", "col1": "District 1 Central Hub", "col2": "1,120", "col3": "1,092", "col4": "28", "chartVal": 1120},
            {"label": "D7", "col1": "District 7 Phu My Hung Hub", "col2": "890", "col3": "865", "col4": "25", "chartVal": 890},
            {"label": "TD", "col1": "Thu Duc Campus Hub", "col2": "780", "col3": "754", "col4": "26", "chartVal": 780},
            {"label": "BT", "col1": "Binh Thanh Hub", "col2": "630", "col3": "607", "col4": "23", "chartVal": 630},
        ],
    }


@router.get("/delivery")
def get_delivery_report(
    start_date: date = Query(default=date(2026, 11, 1)),
    end_date: date = Query(default=date(2026, 11, 15)),
):
    _validate_dates(start_date, end_date)
    return {
        "kpis": [
            {"label": "Total Deliveries", "value": "3,318"},
            {"label": "On-Time Rate", "value": "94.6%"},
            {"label": "Avg. Delivery Time", "value": "24 mins"},
        ],
        "totalSummary": "Total: 3,318 deliveries · 94.6% on-time",
        "rows": [
            {"label": "01", "col1": "01 Nov 2026", "col2": "188", "col3": "179 (95.2%)", "col4": "24 mins", "chartVal": 95.2},
            {"label": "02", "col1": "02 Nov 2026", "col2": "204", "col3": "195 (95.6%)", "col4": "23 mins", "chartVal": 95.6},
            {"label": "03", "col1": "03 Nov 2026", "col2": "218", "col3": "204 (93.6%)", "col4": "25 mins", "chartVal": 93.6},
            {"label": "04", "col1": "04 Nov 2026", "col2": "234", "col3": "222 (94.9%)", "col4": "24 mins", "chartVal": 94.9},
            {"label": "05", "col1": "05 Nov 2026", "col2": "272", "col3": "257 (94.5%)", "col4": "24 mins", "chartVal": 94.5},
            {"label": "06", "col1": "06 Nov 2026", "col2": "326", "col3": "304 (93.3%)", "col4": "26 mins", "chartVal": 93.3},
            {"label": "07", "col1": "07 Nov 2026", "col2": "295", "col3": "278 (94.2%)", "col4": "25 mins", "chartVal": 94.2},
            {"label": "08", "col1": "08 Nov 2026", "col2": "172", "col3": "166 (96.5%)", "col4": "22 mins", "chartVal": 96.5},
        ],
    }