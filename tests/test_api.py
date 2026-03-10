"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_returns_professional_response(self, client: TestClient) -> None:
        """Test that root endpoint returns professional API response."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["message"] == "Wilayah Indonesia API"
        assert "version" in data
        assert data["version"] == "2.0.0"
        assert "docs" in data
        assert "/docs" in data["docs"]
        assert "endpoints" in data
        assert "provinsi" in data["endpoints"]
        assert "search_by_code" in data["endpoints"]

    def test_root_contains_docs_link(self, client: TestClient) -> None:
        """Test that root endpoint contains docs link instead of daftar-provinsi."""
        response = client.get("/")
        data = response.json()

        # Should have 'docs' key
        assert "docs" in data
        # Should NOT have 'daftar-provinsi' key
        assert "daftar-provinsi" not in data


class TestProvinsiEndpoint:
    """Tests for provinsi listing endpoint."""

    def test_list_provinsi_success(self, client: TestClient) -> None:
        """Test successful retrieval of provinsi list."""
        response = client.get("/0")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        # Check first item structure
        first = data[0]
        assert "kode" in first
        assert "nama" in first
        assert "tingkat" in first
        assert first["tingkat"] == 1


class TestKabupatenEndpoint:
    """Tests for kabupaten listing endpoint."""

    def test_list_kabupaten_success(self, client: TestClient) -> None:
        """Test successful retrieval of kabupaten list."""
        response = client.get("/11")  # Aceh
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        # Check structure
        first = data[0]
        assert "kode" in first
        assert "nama" in first
        assert "tingkat" in first
        assert "provinsi" in first
        assert first["tingkat"] == 2
        assert first["provinsi"] == 11

    def test_list_kabupaten_not_found(self, client: TestClient) -> None:
        """Test 404 when provinsi doesn't exist."""
        response = client.get("/999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestKecamatanEndpoint:
    """Tests for kecamatan listing endpoint."""

    def test_list_kecamatan_success(self, client: TestClient) -> None:
        """Test successful retrieval of kecamatan list."""
        response = client.get("/11/1101")  # Aceh / Aceh Selatan
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

        if len(data) > 0:
            first = data[0]
            assert "kode" in first
            assert "nama" in first
            assert "tingkat" in first
            assert "kabupaten" in first
            assert first["tingkat"] == 3

    def test_list_kecamatan_provinsi_not_found(self, client: TestClient) -> None:
        """Test 404 when provinsi doesn't exist."""
        response = client.get("/999/1101")
        assert response.status_code == 404

    def test_list_kecamatan_kabupaten_not_found(self, client: TestClient) -> None:
        """Test 404 when kabupaten doesn't exist."""
        response = client.get("/11/9999")
        assert response.status_code == 404


class TestDesaEndpoint:
    """Tests for desa listing endpoint."""

    def test_list_desa_success(self, client: TestClient) -> None:
        """Test successful retrieval of desa list."""
        response = client.get("/11/1101/110101")  # Aceh / Aceh Selatan / Bakongan
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

        if len(data) > 0:
            first = data[0]
            assert "kode" in first
            assert "nama" in first
            assert "tingkat" in first
            assert "kecamatan" in first
            assert first["tingkat"] == 4

    def test_list_desa_not_found(self, client: TestClient) -> None:
        """Test 404 when kecamatan doesn't exist."""
        response = client.get("/11/1101/999999")
        assert response.status_code == 404


class TestSearchByCodeEndpoint:
    """Tests for the new /kode/{kode} endpoint."""

    def test_search_provinsi_by_code(self, client: TestClient) -> None:
        """Test searching for provinsi by code."""
        response = client.get("/kode/11")
        assert response.status_code == 200
        data = response.json()

        assert data["kode"] == 11
        assert "nama" in data
        assert data["tingkat"] == 1

    def test_search_kabupaten_by_code(self, client: TestClient) -> None:
        """Test searching for kabupaten by code."""
        response = client.get("/kode/1101")
        assert response.status_code == 200
        data = response.json()

        assert data["kode"] == 1101
        assert "nama" in data
        assert data["tingkat"] == 2
        assert "provinsi" in data

    def test_search_kecamatan_by_code(self, client: TestClient) -> None:
        """Test searching for kecamatan by code."""
        response = client.get("/kode/110101")
        assert response.status_code == 200
        data = response.json()

        assert data["kode"] == 110101
        assert "nama" in data
        assert data["tingkat"] == 3
        assert "kabupaten" in data

    def test_search_desa_by_code(self, client: TestClient) -> None:
        """Test searching for desa by code - the main requirement."""
        response = client.get("/kode/1101012001")
        assert response.status_code == 200
        data = response.json()

        assert data["kode"] == 1101012001
        assert "nama" in data
        assert data["tingkat"] == 4
        assert "kecamatan" in data

    def test_search_by_code_not_found(self, client: TestClient) -> None:
        """Test 404 when code doesn't exist."""
        response = client.get("/kode/999999999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_search_invalid_code(self, client: TestClient) -> None:
        """Test validation for invalid code."""
        response = client.get("/kode/0")
        assert response.status_code == 422  # Validation error

    def test_search_negative_code(self, client: TestClient) -> None:
        """Test validation for negative code."""
        response = client.get("/kode/-1")
        assert response.status_code == 422  # Validation error


class TestResponseStructure:
    """Tests for response structure and data integrity."""

    def test_all_endpoints_use_json(self, client: TestClient) -> None:
        """Test that all endpoints return JSON."""
        endpoints = [
            "/",
            "/0",
            "/11",
            "/11/1101",
            "/kode/11",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.headers["content-type"] == "application/json"

    def test_error_responses_have_detail(self, client: TestClient) -> None:
        """Test that error responses have proper structure."""
        error_endpoints = [
            "/999",  # Invalid provinsi
            "/11/9999",  # Invalid kabupaten
            "/kode/999999999",  # Invalid code
        ]

        for endpoint in error_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [404, 422]
            data = response.json()
            assert "detail" in data
