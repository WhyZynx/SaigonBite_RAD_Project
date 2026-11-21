from pathlib import Path
import sys
import json
from io import BytesIO
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import delivery_fee_service as delivery


class FakeQuery:
    def __init__(self, hub):
        self.hub = hub

    def filter(self, *_args):
        return self

    def first(self):
        return self.hub


class FakeDb:
    def __init__(self, hub=None):
        self.hub = hub or SimpleNamespace(address="Hub origin, Ho Chi Minh City", status="OPEN")

    def query(self, _model):
        return FakeQuery(self.hub)


@pytest.fixture(autouse=True)
def clear_delivery_caches(monkeypatch):
    delivery._geocode.cache_clear()
    delivery._geocode_customer_address.cache_clear()
    delivery._hub_coordinates.cache_clear()
    delivery._route_distance_meters.cache_clear()
    monkeypatch.setattr(delivery.time, "sleep", lambda _seconds: None)
    yield
    delivery._geocode.cache_clear()
    delivery._geocode_customer_address.cache_clear()
    delivery._hub_coordinates.cache_clear()
    delivery._route_distance_meters.cache_clear()


def mock_osm(monkeypatch, meters=4_000, *, bad_address=None, route_code="Ok"):
    requests = []

    def fake_get_json(url, provider):
        requests.append(url)
        if url.startswith(delivery.NOMINATIM_URL):
            address = parse_qs(urlparse(url).query)["q"][0]
            if address == bad_address:
                data = []
            elif address.startswith("Hub"):
                data = [{"lat": "10.0", "lon": "20.0"}]
            else:
                data = [
                {"lat": "30.0", "lon": "40.0"}
            ]
        else:
            data = {"code": route_code, "routes": [{"distance": meters}] if route_code == "Ok" else []}
        return delivery.JsonResponse(200, json.dumps(data), data)

    monkeypatch.setattr(delivery, "_get_json", fake_get_json)
    return requests


def test_nominatim_then_osrm_uses_lon_lat_order_and_returns_fee(monkeypatch):
    requests = mock_osm(monkeypatch, meters=4_000)
    result = delivery.DeliveryFeeService(FakeDb()).calculate(1, "Customer address")
    assert result == {"delivery_distance_km": 4.0, "delivery_fee": 20_000, "surcharge": 0}
    assert "q=Hub+origin%2C+Ho+Chi+Minh+City" in requests[0]
    assert "q=Customer+address" in requests[1]
    assert "format=jsonv2" in requests[0] and "countrycodes=vn" in requests[0] and "limit=1" in requests[0]
    assert requests[2] == (
        f"{delivery.OSRM_URL}/20.0,10.0;40.0,30.0?overview=false"
    )


def test_reported_addresses_retry_simpler_hub_query(monkeypatch):
    hub_address = "128 Nguyen Hue, District 1, Ho Chi Minh City"
    customer_address = "12 Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh"
    requests = []

    def geocode_queries(url, provider):
        requests.append(url)
        if url.startswith(delivery.NOMINATIM_URL):
            params = parse_qs(urlparse(url).query)
            query = params.get("q", [None])[0]
            if query in {hub_address, customer_address}:
                data = []
            elif query == "128 Nguyen Hue, Ho Chi Minh City, Vietnam":
                data = [{"lat": "10.7758856", "lon": "106.7014259"}]
            elif params.get("street") == ["Nguyen Hue"] and params.get("house_number") == ["12"]:
                data = [{"lat": "10.7734610", "lon": "106.7040781"}]
            else:
                pytest.fail(f"Unexpected geocoding query: {params}")
            return delivery.JsonResponse(200, json.dumps(data), data)
        data = {"code": "Ok", "routes": [{"distance": 395.1}]}
        return delivery.JsonResponse(200, json.dumps(data), data)

    monkeypatch.setattr(delivery, "_get_json", geocode_queries)
    hub = SimpleNamespace(address=hub_address, status="OPEN")
    result = delivery.DeliveryFeeService(FakeDb(hub)).calculate(1, customer_address)
    assert result == {"delivery_distance_km": 0.395, "delivery_fee": 11_000, "surcharge": 0}
    assert [parse_qs(urlparse(url).query).get("q", [None])[0] for url in requests[:3]] == [
        hub_address,
        "128 Nguyen Hue, Ho Chi Minh City, Vietnam",
        customer_address,
    ]
    customer_structured = parse_qs(urlparse(requests[3]).query)
    assert customer_structured["street"] == ["Nguyen Hue"]
    assert customer_structured["house_number"] == ["12"]
    assert customer_structured["countrycodes"] == ["vn"]
    assert requests[4] == f"{delivery.OSRM_URL}/106.7014259,10.7758856;106.7040781,10.773461?overview=false"
    request_count = len(requests)
    assert delivery._hub_coordinates(hub_address) == (10.7758856, 106.7014259)
    assert len(requests) == request_count


@pytest.mark.parametrize(("meters", "fee", "surcharge"), [
    (4_999, 23_000, 0),
    (5_000, 23_000, 0),
    (5_001, 23_000, 3_000),
    (10_000, 35_000, 3_000),
])
def test_pricing_thresholds_and_exact_ten_km(monkeypatch, meters, fee, surcharge):
    mock_osm(monkeypatch, meters=meters)
    result = delivery.DeliveryFeeService(FakeDb()).calculate(1, "Customer address")
    assert result["delivery_fee"] == fee
    assert result["surcharge"] == surcharge


def test_invalid_address_and_unavailable_route_are_rejected(monkeypatch):
    mock_osm(monkeypatch, bad_address="Unknown destination")
    with pytest.raises(HTTPException) as invalid:
        delivery.DeliveryFeeService(FakeDb()).calculate(1, "Unknown destination")
    assert invalid.value.status_code == 400

    mock_osm(monkeypatch, route_code="NoRoute")
    with pytest.raises(HTTPException) as no_route:
        delivery.DeliveryFeeService(FakeDb()).calculate(1, "Customer address")
    assert no_route.value.status_code == 400


def test_route_failure_and_distance_over_ten_km(monkeypatch):
    def fail_osrm(url, provider):
        if url.startswith(delivery.NOMINATIM_URL):
            data = [{"lat": "10.0", "lon": "20.0"}]
            return delivery.JsonResponse(200, json.dumps(data), data)
        raise delivery.ProviderRequestError("Could not connect to OSRM: service unavailable")

    monkeypatch.setattr(delivery, "_get_json", fail_osrm)
    with pytest.raises(HTTPException) as unavailable:
        delivery.DeliveryFeeService(FakeDb()).calculate(1, "Customer address")
    assert unavailable.value.status_code == 502

    mock_osm(monkeypatch, meters=10_001)
    with pytest.raises(HTTPException) as too_far:
        delivery.DeliveryFeeService(FakeDb()).calculate(1, "Customer address")
    assert too_far.value.status_code == 400


def test_nominatim_uses_identifying_user_agent(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b'[{"lat":"10","lon":"20"}]'

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(delivery, "urlopen", fake_urlopen)
    delivery._get_json(f"{delivery.NOMINATIM_URL}?q=Hub&format=jsonv2&countrycodes=vn&limit=1", "Nominatim")
    assert captured["request"].get_header("User-agent") == delivery.USER_AGENT
    assert "SaigonBite" in delivery.USER_AGENT


def test_nominatim_http_status_and_body_are_logged(caplog, monkeypatch):
    def failed_request(_request, timeout):
        raise delivery.HTTPError(
            "https://nominatim.openstreetmap.org/search", 429, "Too Many Requests", None,
            BytesIO(b"rate limit response body"),
        )

    monkeypatch.setattr(delivery, "urlopen", failed_request)
    with pytest.raises(delivery.ProviderRequestError):
        delivery._get_json("https://nominatim.openstreetmap.org/search?q=Hub", "Nominatim")
    assert "status=429" in caplog.text
    assert "rate limit response body" in caplog.text
