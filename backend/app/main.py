from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.repositories.mock_orders import orders
from app.routers.kitchen import router as kitchen_router
from app.schemas import OrderDetail

app = FastAPI(title="SaigonBite Kitchen API", version="0.1.0")
app.include_router(kitchen_router)


@app.get("/api/orders/{order_id}", response_model=OrderDetail, tags=["Orders"])
def get_order_detail(order_id: int):
    """TEMPORARY mock-compatible implementation; replace with TV1 order service."""
    return orders.get(order_id)


frontend_dir = Path(__file__).resolve().parents[2] / "frontend" / "kitchen"
app.mount("/", StaticFiles(directory=frontend_dir.resolve(), html=True), name="kitchen-ui")
