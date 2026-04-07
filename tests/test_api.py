"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestRootAndOpenAPITags:
    def test_root_groups_are_exposed(self, client: TestClient) -> None:
        response = client.get("/api/")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Wilayah Indonesia API"
        assert data["version"] == "3.0.0"
        assert "groups" in data
        assert "root" in data["groups"]
        assert "search" in data["groups"]
        assert "wilayah" in data["groups"]
        assert "simple" in data["groups"]

    def test_openapi_has_required_tag_sections(self, client: TestClient) -> None:
        response = client.get("/openapi.json")
        assert response.status_code == 200

        payload = response.json()
        tag_names = {tag["name"] for tag in payload.get("tags", [])}
        assert {"root", "search", "wilayah", "simple"}.issubset(tag_names)


class TestWilayahLegacyRules:
    def test_provinsi_listing(self, client: TestClient) -> None:
        response = client.get("/api/0")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["tingkat"] == 1

    def test_kabupaten_listing(self, client: TestClient) -> None:
        response = client.get("/api/11")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["tingkat"] == 2
        assert data[0].get("parent") is None

    def test_kecamatan_listing(self, client: TestClient) -> None:
        response = client.get("/api/11/1101")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        if data:
            assert data[0]["tingkat"] == 3

    def test_desa_listing(self, client: TestClient) -> None:
        response = client.get("/api/11/1101/110101")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        if data:
            assert data[0]["tingkat"] == 4

    def test_invalid_wilayah_segment_returns_422(self, client: TestClient) -> None:
        response = client.get("/api/11/1")
        assert response.status_code == 422


class TestSearchRules:
    def test_search_by_code_success(self, client: TestClient) -> None:
        response = client.get("/api/kode/110101")
        assert response.status_code == 200

        data = response.json()
        assert data["kode"] == 110101
        assert data["tingkat"] == 3

    def test_search_not_found(self, client: TestClient) -> None:
        response = client.get("/api/kode/999999999")
        assert response.status_code == 404
        assert "detail" in response.json()


class TestSimpleRules:
    def test_simple_prefix_tingkat_1(self, client: TestClient) -> None:
        response = client.get("/api/s/11")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["tingkat"] == 1
        assert data["data"]["level"] == "provinsi"
        assert data["data"]["kode_singkat"] == "11"

    def test_simple_prefix_tingkat_2(self, client: TestClient) -> None:
        response = client.get("/api/s/11/1")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["tingkat"] == 2
        assert data["data"]["kode_lengkap"] == 1101
        assert data["data"]["kode_singkat"] == "11/01"

    def test_simple_prefix_tingkat_3(self, client: TestClient) -> None:
        response = client.get("/api/s/11/1/1")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["tingkat"] == 3
        assert data["data"]["kode_lengkap"] == 110101
        assert data["data"]["kode_singkat"] == "11/01/01"

    def test_simple_zero_padded_response(self, client: TestClient) -> None:
        response = client.get("/api/s/11/1/1")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["tingkat"] == 3
        assert data["data"]["kode_lengkap"] == 110101

    def test_simple_not_found_response(self, client: TestClient) -> None:
        response = client.get("/api/s/99/1/1")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
