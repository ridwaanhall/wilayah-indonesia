"""Tests for API endpoints."""

from typing import Any, cast

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from prod.main import app

SETTINGS = get_settings()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def assert_meta(meta: dict[str, object]) -> None:
    assert meta["api_version"] == SETTINGS.api_version
    assert isinstance(meta["timestamp"], str)
    assert isinstance(meta["request_id"], str)
    assert isinstance(meta["duration_ms"], int)
    assert meta["duration_ms"] >= 0


def assert_envelope(payload: dict[str, object], success: bool) -> None:
    assert payload["success"] is success
    assert "data" in payload
    assert "error" in payload
    assert "meta" in payload
    assert_meta(cast(dict[str, Any], payload["meta"]))


def assert_region_shape(region: dict[str, object]) -> None:
    assert isinstance(region["code"], int)
    assert isinstance(region["short_code"], str)
    assert isinstance(region["name"], str)
    assert region["depth"] in (1, 2, 3, 4)
    assert region["type"] in ("province", "regency", "district", "village")
    assert isinstance(region["has_children"], bool)
    assert "parent" in region


def assert_error_shape(error: dict[str, object], expected_code: str) -> None:
    assert error["code"] == expected_code
    assert isinstance(error["message"], str)
    assert isinstance(error["detail"], str)
    assert isinstance(error["hint"], str)
    assert isinstance(error["docs"], str)
    assert error["docs"].endswith(f"/docs/errors#{expected_code}")
    assert "fields" in error


class TestRootAndOpenAPITags:
    def test_landing_page_is_server_rendered_with_seo(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "script-src 'self'" in response.headers["content-security-policy"]

        body = response.text
        assert '<meta name="description"' in body
        assert '<meta property="og:title"' in body
        assert '<link rel="canonical" href="https://wilayah.rone.dev/">' in body
        assert '"@type": "Dataset"' in body
        assert "83,731" in body  # totals are rendered on the server, not by JavaScript
        assert "/api/kode/3301012001" in body  # reference table uses the endpoint examples
        assert body.count('role="combobox"') == 4
        assert '<html lang="en" data-theme="dark">' in body  # dark is the default theme
        assert "data-theme-toggle" in body
        assert "rone.dev/static" not in body  # icons are served locally

    def test_favicon_is_served_locally(self, client: TestClient) -> None:
        response = client.get("/favicon.ico")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/x-icon"
        assert response.content[:4] == bytes([0, 0, 1, 0])  # ICO header
        assert client.get("/static/favicon.svg").status_code == 200
        assert client.get("/static/apple-touch-icon.png").status_code == 200
        assert "https://rone.dev" not in client.get("/").headers["content-security-policy"]

    def test_static_assets_are_served(self, client: TestClient) -> None:
        assert client.get("/static/app.css").status_code == 200
        assert "javascript" in client.get("/static/app.js").headers["content-type"]
        assert "javascript" in client.get("/static/theme.js").headers["content-type"]

    def test_error_catalog_page_has_anchor_per_code(self, client: TestClient) -> None:
        response = client.get("/docs/errors")
        assert response.status_code == 200
        for code in ("INVALID_REGION_CODE", "REGION_NOT_FOUND", "VILLAGE_NOT_FOUND", "VALIDATION_FAILED"):
            assert f'id="{code}"' in response.text

    def test_robots_and_sitemap(self, client: TestClient) -> None:
        robots = client.get("/robots.txt")
        assert robots.status_code == 200
        assert "Sitemap: https://wilayah.rone.dev/sitemap.xml" in robots.text

        sitemap = client.get("/sitemap.xml")
        assert sitemap.headers["content-type"].startswith("application/xml")
        assert "<loc>https://wilayah.rone.dev/docs/errors</loc>" in sitemap.text

    def test_unknown_path_and_method_use_generic_codes(self, client: TestClient) -> None:
        missing = client.get("/nope")
        assert missing.status_code == 404
        assert_error_shape(missing.json()["error"], "RESOURCE_NOT_FOUND")

        wrong_method = client.post("/api/0")
        assert wrong_method.status_code == 405
        assert_error_shape(wrong_method.json()["error"], "METHOD_NOT_ALLOWED")

    def test_root_groups_are_exposed(self, client: TestClient) -> None:
        response = client.get("/api/")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        data = payload["data"]

        assert data["name"] == "Wilayah Indonesia API"
        assert data["version"] == "3.0.0"
        assert "groups" in data
        assert "root" in data["groups"]
        assert "search" in data["groups"]
        assert "wilayah" in data["groups"]
        assert "simple" in data["groups"]
        assert "/api/stats/{kode}" in data["groups"]["stats"]

    def test_health_endpoint(self, client: TestClient) -> None:
        response = client.get("/api/health")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        assert payload["data"]["status"] == "ok"
        assert payload["data"]["version"] == SETTINGS.api_version

    def test_openapi_has_required_tag_sections(self, client: TestClient) -> None:
        response = client.get("/openapi.json")
        assert response.status_code == 200

        payload = response.json()
        tag_names = {tag["name"] for tag in payload.get("tags", [])}
        assert {"root", "search", "stats", "wilayah", "simple"}.issubset(tag_names)


class TestWilayahLegacyRules:
    def test_provinsi_listing(self, client: TestClient) -> None:
        response = client.get("/api/0")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)

        data = payload["data"]
        assert "items" in data
        assert "pagination" in data
        assert len(data["items"]) > 0
        assert_region_shape(data["items"][0])
        assert data["items"][0]["depth"] == 1
        assert data["items"][0]["parent"] is None

    def test_kabupaten_listing(self, client: TestClient) -> None:
        response = client.get("/api/11")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        items = payload["data"]["items"]

        assert len(items) > 0
        assert_region_shape(items[0])
        assert items[0]["depth"] == 2
        assert items[0]["parent"] is None

    def test_parent_query_flag_keeps_same_shape(self, client: TestClient) -> None:
        without_parent = client.get("/api/11/1101")
        with_parent = client.get("/api/11/1101?parent=true")

        assert without_parent.status_code == 200
        assert with_parent.status_code == 200

        items_without = without_parent.json()["data"]["items"]
        items_with = with_parent.json()["data"]["items"]
        assert len(items_without) == len(items_with)

        if items_without and items_with:
            assert set(items_without[0].keys()) == set(items_with[0].keys())
            assert items_without[0]["parent"] is None
            assert items_with[0]["parent"] is not None
            assert items_with[0]["parent"]["depth"] == 2
            assert items_with[0]["parent"]["parent"] is None

    def test_provinsi_parent_query_keeps_parent_null(self, client: TestClient) -> None:
        without_parent = client.get("/api/0?parent=false")
        with_parent = client.get("/api/0?parent=true")

        assert without_parent.status_code == 200
        assert with_parent.status_code == 200

        first_without = without_parent.json()["data"]["items"][0]
        first_with = with_parent.json()["data"]["items"][0]
        assert set(first_without.keys()) == set(first_with.keys())
        assert first_without["parent"] is None
        assert first_with["parent"] is None

    def test_kecamatan_listing(self, client: TestClient) -> None:
        response = client.get("/api/11/1101?parent=true")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        items = payload["data"]["items"]
        if items:
            assert items[0]["depth"] == 3
            assert items[0]["parent"] is not None
            assert items[0]["parent"]["depth"] == 2
            assert items[0]["parent"]["parent"] is None

    def test_desa_listing(self, client: TestClient) -> None:
        response = client.get("/api/11/1101/110101?parent=true")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        items = payload["data"]["items"]
        if items:
            assert items[0]["depth"] == 4
            assert items[0]["parent"] is not None
            assert items[0]["parent"]["depth"] == 3
            assert items[0]["parent"]["parent"] is None

    def test_invalid_wilayah_segment_returns_422(self, client: TestClient) -> None:
        response = client.get("/api/11/1")
        assert response.status_code == 422

        payload = response.json()
        assert_envelope(payload, success=False)
        assert_error_shape(payload["error"], "INVALID_REGION_CODE")
        assert payload["error"]["fields"] is not None


class TestSearchRules:
    def test_search_by_code_success(self, client: TestClient) -> None:
        response = client.get("/api/kode/110101")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        data = payload["data"]

        assert data["code"] == 110101
        assert data["depth"] == 3
        assert data["parent"]["code"] == 1101
        assert data["parent"]["parent"]["code"] == 11
        assert data["parent"]["parent"]["parent"] is None

    def test_search_village_full_chain(self, client: TestClient) -> None:
        response = client.get("/api/kode/1101012001")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        data = payload["data"]

        assert data["depth"] == 4
        assert data["parent"]["depth"] == 3
        assert data["parent"]["parent"]["depth"] == 2
        assert data["parent"]["parent"]["parent"]["depth"] == 1
        assert data["parent"]["parent"]["parent"]["parent"] is None

    def test_search_invalid_code_length(self, client: TestClient) -> None:
        response = client.get("/api/kode/123")
        assert response.status_code == 422

        payload = response.json()
        assert_envelope(payload, success=False)
        assert_error_shape(payload["error"], "INVALID_REGION_CODE")
        assert payload["error"]["fields"] is not None

    def test_search_not_found(self, client: TestClient) -> None:
        response = client.get("/api/kode/9999999999")
        assert response.status_code == 404

        payload = response.json()
        assert_envelope(payload, success=False)
        assert_error_shape(payload["error"], "REGION_NOT_FOUND")

    def test_search_parent_query_flag(self, client: TestClient) -> None:
        without_parent = client.get("/api/kode/110101?parent=false")
        with_parent = client.get("/api/kode/110101?parent=true")

        assert without_parent.status_code == 200
        assert with_parent.status_code == 200

        data_without = without_parent.json()["data"]
        data_with = with_parent.json()["data"]

        assert set(data_without.keys()) == set(data_with.keys())
        assert data_without["parent"] is None
        assert data_with["parent"] is not None


class TestSimpleRules:
    def test_simple_prefix_tingkat_1(self, client: TestClient) -> None:
        response = client.get("/api/s/11")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        assert payload["data"]["depth"] == 1
        assert payload["data"]["type"] == "province"
        assert payload["data"]["short_code"] == "11"
        assert payload["data"]["parent"] is None

    def test_simple_prefix_tingkat_2(self, client: TestClient) -> None:
        response = client.get("/api/s/11/1")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        assert payload["data"]["depth"] == 2
        assert payload["data"]["code"] == 1101
        assert payload["data"]["short_code"] == "11/01"
        assert payload["data"]["parent"]["code"] == 11
        assert payload["data"]["parent"]["parent"] is None

    def test_simple_prefix_tingkat_3(self, client: TestClient) -> None:
        response = client.get("/api/s/11/1/1")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        assert payload["data"]["depth"] == 3
        assert payload["data"]["code"] == 110101
        assert payload["data"]["short_code"] == "11/01/01"
        assert payload["data"]["parent"]["depth"] == 2
        assert payload["data"]["parent"]["parent"]["depth"] == 1
        assert payload["data"]["parent"]["parent"]["parent"] is None

    def test_simple_prefix_tingkat_4(self, client: TestClient) -> None:
        response = client.get("/api/s/11/1/1/2001")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        assert payload["data"]["depth"] == 4
        assert payload["data"]["code"] == 1101012001
        assert payload["data"]["short_code"] == "11/01/01/2001"
        assert payload["data"]["parent"]["depth"] == 3
        assert payload["data"]["parent"]["parent"]["depth"] == 2
        assert payload["data"]["parent"]["parent"]["parent"]["depth"] == 1

    def test_simple_not_found_response(self, client: TestClient) -> None:
        response = client.get("/api/s/99/1/1")
        assert response.status_code == 404

        payload = response.json()
        assert_envelope(payload, success=False)
        assert_error_shape(payload["error"], "PROVINCE_NOT_FOUND")

    def test_simple_validation_response(self, client: TestClient) -> None:
        response = client.get("/api/s/11/1/1/10000")
        assert response.status_code == 422

        payload = response.json()
        assert_envelope(payload, success=False)
        assert_error_shape(payload["error"], "VALIDATION_FAILED")
        assert payload["error"]["fields"] is not None

    @pytest.mark.parametrize(
        "path, expect_parent_when_true",
        [
            ("/api/s/11", False),
            ("/api/s/11/1", True),
            ("/api/s/11/1/1", True),
            ("/api/s/11/1/1/2001", True),
        ],
    )
    def test_simple_parent_query_flag(
        self,
        client: TestClient,
        path: str,
        expect_parent_when_true: bool,
    ) -> None:
        without_parent = client.get(f"{path}?parent=false")
        with_parent = client.get(f"{path}?parent=true")

        assert without_parent.status_code == 200
        assert with_parent.status_code == 200

        data_without = without_parent.json()["data"]
        data_with = with_parent.json()["data"]

        assert set(data_without.keys()) == set(data_with.keys())
        assert data_without["parent"] is None

        if expect_parent_when_true:
            assert data_with["parent"] is not None
        else:
            assert data_with["parent"] is None


class TestStatsRules:
    def test_national_stats(self, client: TestClient) -> None:
        response = client.get("/api/stats/0")
        assert response.status_code == 200

        payload = response.json()
        assert_envelope(payload, success=True)
        data = payload["data"]
        assert data["region"] is None
        assert data["levels"] == {"province": 38, "regency": 514, "district": 7277, "village": 83731}
        assert len(data["children"]) == 38
        assert sum(child["levels"]["village"] for child in data["children"]) == 83731

    def test_province_stats_children_sum_to_parent(self, client: TestClient) -> None:
        data = client.get("/api/stats/33").json()["data"]
        assert data["region"]["code"] == 33
        assert data["levels"]["province"] == 0
        assert data["kinds"]["kabupaten"] + data["kinds"]["kota"] == data["levels"]["regency"]
        for level in ("district", "village"):
            assert sum(child["levels"][level] for child in data["children"]) == data["levels"][level]
        assert_region_shape(data["children"][0]["region"])

    def test_region_stats_carry_full_parent_chain(self, client: TestClient) -> None:
        data = client.get("/api/stats/330101").json()["data"]
        assert data["region"]["parent"]["parent"]["code"] == 33
        assert all(child["region"]["type"] == "village" for child in data["children"])

    def test_stats_invalid_and_missing_codes(self, client: TestClient) -> None:
        invalid = client.get("/api/stats/123")
        assert invalid.status_code == 422
        assert_error_shape(invalid.json()["error"], "INVALID_REGION_CODE")

        missing = client.get("/api/stats/99")
        assert missing.status_code == 404
        assert_error_shape(missing.json()["error"], "REGION_NOT_FOUND")
