"""OpenStreetMap geocoding and OSRM delivery distance calculations."""

from __future__ import annotations

import json
import logging
import math
import os
import socket
import threading
import time
from dataclasses import dataclass
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Hub

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
USER_AGENT = "SaigonBite/1.0 (customer delivery distance service)"
MAX_DELIVERY_DISTANCE_KM = 10.0
BASE_FEE_VND = 10_000
PRICE_PER_KM_VND = 2_500
DISTANCE_SURCHARGE_VND = 3_000
DEMO_DELIVERY_DISTANCE_KM = float(os.getenv("DELIVERY_DEMO_DISTANCE_KM", "3.0"))
DEMO_DELIVERY_FEE_VND = int(os.getenv("DELIVERY_DEMO_FEE_VND", "18_000"))
DEMO_DELIVERY_SURCHARGE_VND = int(os.getenv("DELIVERY_DEMO_SURCHARGE_VND", "0"))
NOMINATIM_MIN_INTERVAL_SECONDS = 1.0
OSRM_MIN_INTERVAL_SECONDS = 1.0

_nominatim_lock = threading.Lock()
_last_nominatim_request = 0.0
_osrm_lock = threading.Lock()
_last_osrm_request = 0.0


@dataclass
class JsonResponse:
    status: int
    body: str
    data: object


class ProviderRequestError(Exception):
    pass


class ProviderTimeout(ProviderRequestError):
    pass


class ProviderMalformedResponse(ProviderRequestError):
    pass


class NoGeocodingResult(Exception):
    pass


def _get_json(url: str, provider: str) -> JsonResponse:
    """Fetch JSON while retaining status/body for useful diagnostics."""
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=12) as response:
            status = getattr(response, "status", 200)
            body = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        logger.error("%s HTTP failure: status=%s body=%s", provider, exc.code, body)
        raise ProviderRequestError(f"{provider} returned HTTP {exc.code}: {body[:400]}") from exc
    except (TimeoutError, socket.timeout) as exc:
        logger.error("%s request timed out: %s", provider, exc)
        raise ProviderTimeout(f"{provider} request timed out") from exc
    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, (TimeoutError, socket.timeout)):
            logger.error("%s request timed out: %s", provider, reason)
            raise ProviderTimeout(f"{provider} request timed out") from exc
        logger.error("%s connection failed: %s", provider, reason)
        raise ProviderRequestError(f"Could not connect to {provider}: {reason}") from exc
    except OSError as exc:
        logger.error("%s request failed: %s", provider, exc)
        raise ProviderRequestError(f"{provider} request failed: {exc}") from exc

    try:
        data = json.loads(body)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("%s malformed response: status=%s body=%s", provider, status, body)
        raise ProviderMalformedResponse(
            f"{provider} returned malformed JSON (HTTP {status})"
        ) from exc
    return JsonResponse(status=status, body=body, data=data)


def _pace_nominatim() -> None:
    global _last_nominatim_request
    with _nominatim_lock:
        wait = NOMINATIM_MIN_INTERVAL_SECONDS - (time.monotonic() - _last_nominatim_request)
        if wait > 0:
            time.sleep(wait)
        _last_nominatim_request = time.monotonic()


def _geocode_params(params: dict[str, str]) -> tuple[float, float]:
    """Fetch and validate coordinates; only successful results are cached by callers."""
    _pace_nominatim()
    query = urlencode({**params, "format": "jsonv2", "countrycodes": "vn", "limit": 1})
    response = _get_json(f"{NOMINATIM_URL}?{query}", "Nominatim")
    results = response.data
    if not isinstance(results, list) or not results:
        logger.warning("Nominatim geocoding returned no results: status=%s body=%s", response.status, response.body)
        raise NoGeocodingResult("Nominatim returned no matching address")
    if not isinstance(results[0], dict):
        logger.error("Nominatim malformed result: status=%s body=%s", response.status, response.body)
        raise ProviderMalformedResponse("Nominatim returned a malformed address result")
    try:
        latitude = float(results[0]["lat"])
        longitude = float(results[0]["lon"])
    except (KeyError, TypeError, ValueError) as exc:
        logger.error("Nominatim result lacks valid lat/lon: status=%s body=%s", response.status, response.body)
        raise ProviderMalformedResponse("Nominatim result did not contain valid lat and lon coordinates") from exc
    if not (math.isfinite(latitude) and -90 <= latitude <= 90
            and math.isfinite(longitude) and -180 <= longitude <= 180):
        logger.error("Nominatim returned out-of-range coordinates: status=%s body=%s", response.status, response.body)
        raise ProviderMalformedResponse("Nominatim returned coordinates outside valid ranges")
    return latitude, longitude


@lru_cache(maxsize=512)
def _geocode(address: str) -> tuple[float, float]:
    """Free-form lookup. Successful results only are cached."""
    return _geocode_params({"q": address})


def _geocode_address(address: str) -> tuple[float, float]:
    """Try the street and locality from the supplied address before free-form lookup."""
    parts = [part.strip() for part in address.split(",") if part.strip()]
    if len(parts) > 1:
        street = parts[0]
        localities = list(dict.fromkeys((parts[-1], ", ".join(parts[1:]))))
        for locality in localities:
            try:
                return _geocode_params({
                    "street": street,
                    "city": locality,
                    "country": "Vietnam",
                })
            except NoGeocodingResult:
                continue
    return _geocode(address)


@lru_cache(maxsize=256)
def _hub_coordinates(address: str) -> tuple[float, float]:
    return _geocode_address(address)


@lru_cache(maxsize=512)
def _geocode_customer_address(address: str) -> tuple[float, float]:
    return _geocode_address(address)


@lru_cache(maxsize=512)
def _route_distance_meters(hub_lat: float, hub_lon: float, customer_lat: float, customer_lon: float) -> float:
    global _last_osrm_request
    # OSRM requires longitude,latitude ordering.
    coordinates = f"{hub_lon},{hub_lat};{customer_lon},{customer_lat}"
    url = f"{OSRM_URL}/{coordinates}?overview=false"
    with _osrm_lock:
        wait = OSRM_MIN_INTERVAL_SECONDS - (time.monotonic() - _last_osrm_request)
        if wait > 0:
            time.sleep(wait)
        _last_osrm_request = time.monotonic()
    response = _get_json(url, "OSRM")
    data = response.data
    if not isinstance(data, dict):
        raise ProviderMalformedResponse(f"OSRM returned a malformed response (HTTP {response.status})")
    if data.get("code") != "Ok":
        raise HTTPException(status_code=400, detail=f"OSRM could not find a driving route: {data.get('message') or data.get('code', 'unknown route error')}")
    routes = data.get("routes") or []
    if not isinstance(routes, list) or not routes or not isinstance(routes[0], dict):
        raise HTTPException(status_code=400, detail="OSRM returned no driving route for these addresses")
    distance_meters = routes[0].get("distance")
    if not isinstance(distance_meters, (int, float)) or not math.isfinite(distance_meters) or distance_meters < 0:
        raise ProviderMalformedResponse("OSRM route did not contain a valid distance in meters")
    return float(distance_meters)


def _provider_http_error(exc: ProviderRequestError) -> HTTPException:
    return HTTPException(status_code=502, detail=str(exc))


class DeliveryFeeService:
    def __init__(self, db: Session):
        self.db = db

    def calculate(self, hub_id: int, destination_address: str, *, demo: bool = False) -> dict:
        hub = self.db.query(Hub).filter(Hub.hub_id == hub_id).first()
        if hub is None:
            raise HTTPException(status_code=404, detail="Hub not found")
        if hub.status != "OPEN":
            raise HTTPException(status_code=400, detail="This hub is not accepting orders")
        destination_address = destination_address.strip()
        if not destination_address:
            raise HTTPException(status_code=422, detail="Delivery address is required")

        if demo:
            if not math.isfinite(DEMO_DELIVERY_DISTANCE_KM) or not 0 <= DEMO_DELIVERY_DISTANCE_KM <= MAX_DELIVERY_DISTANCE_KM:
                raise HTTPException(status_code=500, detail="Demo delivery distance must be between 0 and 10 km")
            if DEMO_DELIVERY_FEE_VND < 0 or DEMO_DELIVERY_SURCHARGE_VND < 0:
                raise HTTPException(status_code=500, detail="Demo delivery fees cannot be negative")
            return {"delivery_distance_km": DEMO_DELIVERY_DISTANCE_KM,
                    "delivery_fee": DEMO_DELIVERY_FEE_VND,
                    "surcharge": DEMO_DELIVERY_SURCHARGE_VND,
                    "is_demo": True}

        try:
            hub_coordinates = _hub_coordinates(hub.address)
        except NoGeocodingResult as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except ProviderRequestError as exc:
            raise _provider_http_error(exc) from exc

        try:
            customer_coordinates = _geocode_customer_address(destination_address)
        except NoGeocodingResult as exc:
            raise HTTPException(status_code=400, detail=f"Nominatim found no result for delivery address '{destination_address}'") from exc
        except ProviderRequestError as exc:
            raise _provider_http_error(exc) from exc

        # Both coordinate pairs are validated by _geocode before OSRM is called.
        try:
            distance_meters = _route_distance_meters(
                hub_coordinates[0], hub_coordinates[1],
                customer_coordinates[0], customer_coordinates[1],
            )
        except HTTPException:
            raise
        except ProviderRequestError as exc:
            raise _provider_http_error(exc) from exc

        distance_km = distance_meters / 1000
        if distance_km > MAX_DELIVERY_DISTANCE_KM:
            raise HTTPException(status_code=400, detail="Delivery address is outside the 10 km delivery range")
        surcharge = DISTANCE_SURCHARGE_VND if distance_km > 5 else 0
        delivery_fee = math.ceil((BASE_FEE_VND + distance_km * PRICE_PER_KM_VND) / 1_000) * 1_000
        return {
            "delivery_distance_km": round(distance_km, 3),
            "delivery_fee": int(delivery_fee),
            "surcharge": surcharge,
        }
