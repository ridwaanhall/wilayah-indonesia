"""Schema contract tests for endpoint responses."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from app.api.endpoints.root import HealthData, RootData
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.wilayah import RegionListData, RegionResource
from prod.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _validate(model: Any, payload: dict[str, Any]) -> None:
    TypeAdapter(model).validate_python(payload)


def test_all_success_endpoints_match_declared_schema(client: TestClient) -> None:
    checks: list[tuple[str, Any]] = [
        ("/api/0?parent=false", SuccessResponse[RegionListData]),
        ("/api/0?parent=true", SuccessResponse[RegionListData]),
        ("/api/11?parent=false", SuccessResponse[RegionListData]),
        ("/api/11?parent=true", SuccessResponse[RegionListData]),
        ("/api/11/1101?parent=false", SuccessResponse[RegionListData]),
        ("/api/11/1101?parent=true", SuccessResponse[RegionListData]),
        ("/api/11/1101/110101?parent=false", SuccessResponse[RegionListData]),
        ("/api/11/1101/110101?parent=true", SuccessResponse[RegionListData]),
        ("/api/kode/110101?parent=false", SuccessResponse[RegionResource]),
        ("/api/kode/110101?parent=true", SuccessResponse[RegionResource]),
        ("/api/s/11?parent=false", SuccessResponse[RegionResource]),
        ("/api/s/11?parent=true", SuccessResponse[RegionResource]),
        ("/api/s/11/1?parent=false", SuccessResponse[RegionResource]),
        ("/api/s/11/1?parent=true", SuccessResponse[RegionResource]),
        ("/api/s/11/1/1?parent=false", SuccessResponse[RegionResource]),
        ("/api/s/11/1/1?parent=true", SuccessResponse[RegionResource]),
        ("/api/s/11/1/1/2001?parent=false", SuccessResponse[RegionResource]),
        ("/api/s/11/1/1/2001?parent=true", SuccessResponse[RegionResource]),
        ("/api/?parent=false", SuccessResponse[RootData]),
        ("/api/?parent=true", SuccessResponse[RootData]),
        ("/api/health?parent=false", SuccessResponse[HealthData]),
        ("/api/health?parent=true", SuccessResponse[HealthData]),
    ]

    for path, model in checks:
        response = client.get(path)
        assert response.status_code == 200, path
        _validate(model, response.json())


def test_error_endpoints_match_declared_schema(client: TestClient) -> None:
    checks = [
        "/api/kode/123",        # invalid code length
        "/api/kode/9999999999", # not found
        "/api/11/1",            # invalid segment length
        "/api/s/99/1/1",        # not found
        "/api/s/11/1/1/10000",  # validation error by path constraint
    ]

    for path in checks:
        response = client.get(path)
        assert response.status_code in {404, 422}, path
        _validate(ErrorResponse, response.json())


def test_parent_flag_same_item_keys(client: TestClient) -> None:
    pairs = [
        ("/api/0?parent=false", "/api/0?parent=true"),
        ("/api/11?parent=false", "/api/11?parent=true"),
        ("/api/11/1101?parent=false", "/api/11/1101?parent=true"),
        (
            "/api/11/1101/110101?parent=false",
            "/api/11/1101/110101?parent=true",
        ),
    ]

    for without_parent, with_parent in pairs:
        payload_without = client.get(without_parent).json()
        payload_with = client.get(with_parent).json()

        items_without = payload_without["data"]["items"]
        items_with = payload_with["data"]["items"]
        assert len(items_without) == len(items_with)

        if items_without:
            assert set(items_without[0].keys()) == set(items_with[0].keys())


def test_parent_flag_changes_parent_value_when_parent_exists(client: TestClient) -> None:
    # Provinces have no parent, so parent remains null for both modes.
    province_false = client.get("/api/0?parent=false").json()
    province_true = client.get("/api/0?parent=true").json()
    assert province_false["data"]["items"][0]["parent"] is None
    assert province_true["data"]["items"][0]["parent"] is None

    kab_false = client.get("/api/11?parent=false").json()
    kab_true = client.get("/api/11?parent=true").json()
    assert kab_false["data"]["items"][0]["parent"] is None
    assert kab_true["data"]["items"][0]["parent"] is not None

    kec_false = client.get("/api/11/1101?parent=false").json()
    kec_true = client.get("/api/11/1101?parent=true").json()
    assert kec_false["data"]["items"][0]["parent"] is None
    assert kec_true["data"]["items"][0]["parent"] is not None

    desa_false = client.get("/api/11/1101/110101?parent=false").json()
    desa_true = client.get("/api/11/1101/110101?parent=true").json()
    assert desa_false["data"]["items"][0]["parent"] is None
    assert desa_true["data"]["items"][0]["parent"] is not None


def test_parent_flag_changes_parent_value_for_single_object_routes(client: TestClient) -> None:
    checks = [
        ("/api/kode/110101", "obj"),
        ("/api/s/11", "null"),
        ("/api/s/11/1", "obj"),
        ("/api/s/11/1/1", "obj"),
        ("/api/s/11/1/1/2001", "obj"),
    ]

    for path, expected_when_true in checks:
        payload_false = client.get(f"{path}?parent=false").json()
        payload_true = client.get(f"{path}?parent=true").json()

        data_false = payload_false["data"]
        data_true = payload_true["data"]
        assert set(data_false.keys()) == set(data_true.keys())

        if expected_when_true == "null":
            assert data_false["parent"] is None
            assert data_true["parent"] is None
        else:
            assert data_false["parent"] is None
            assert data_true["parent"] is not None
