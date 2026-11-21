"""Fixed demo delivery routes between supported hubs and delivery zones."""

from fastapi import HTTPException

MAX_DELIVERY_DISTANCE_KM = 10.0

DESTINATIONS = {
    "nguyen-hue": {"address": "18 Nguyen Hue Street, District 1"},
    "ben-thanh": {"address": "45 Le Loi Street, District 1"},
    "war-remnants": {"address": "28 Vo Van Tan Street, District 3"},
    "tdtu-d7": {"address": "19 Nguyen Huu Tho Street, District 7"},
    "thu-duc-center": {"address": "50 Vo Van Ngan Street, Thu Duc City"},
}

# Estimated road distances in km from each seeded hub to each fixed demo destination.
ROUTE_DISTANCES_KM = {
    1: {"nguyen-hue": 1.0, "ben-thanh": 2.8, "war-remnants": 3.6, "tdtu-d7": 9.6},
    2: {"nguyen-hue": 4.4, "ben-thanh": 3.2, "war-remnants": 2.5, "tdtu-d7": 9.7},
    3: {"ben-thanh": 9.1, "war-remnants": 8.6, "tdtu-d7": 1.5},
    4: {"thu-duc-center": 2.0},
}


def delivery_fee_for_distance(distance_km: float) -> int:
    """Simple demo pricing: 15k to 3 km, 20k to 6 km, then 30k to 10 km."""
    if distance_km <= 3:
        return 15_000
    if distance_km <= 6:
        return 20_000
    return 30_000


def get_delivery_route(hub_id: int, destination_id: str) -> dict:
    distance_km = ROUTE_DISTANCES_KM.get(hub_id, {}).get(destination_id)
    destination = DESTINATIONS.get(destination_id)
    if distance_km is None or destination is None or distance_km > MAX_DELIVERY_DISTANCE_KM:
        raise HTTPException(status_code=400, detail="Delivery is not available for this hub and destination")
    return {
        "destination_id": destination_id,
        **destination,
        "distance_km": distance_km,
        "delivery_fee": delivery_fee_for_distance(distance_km),
    }


def list_delivery_routes(hub_id: int) -> list[dict]:
    return [
        get_delivery_route(hub_id, destination_id)
        for destination_id in ROUTE_DISTANCES_KM.get(hub_id, {})
    ]
