"""Tests for DataLoader class."""

from api.loader import DataLoader, get_loader


class TestDataLoader:
    """Tests for DataLoader functionality."""

    def test_singleton_pattern(self) -> None:
        """Test that DataLoader follows singleton pattern."""
        loader1 = DataLoader()
        loader2 = DataLoader()
        assert loader1 is loader2

    def test_get_loader_caching(self) -> None:
        """Test that get_loader returns cached instance."""
        loader1 = get_loader()
        loader2 = get_loader()
        assert loader1 is loader2

    def test_provinsi_list_not_empty(self) -> None:
        """Test that provinsi list is loaded."""
        loader = get_loader()
        assert len(loader.provinsi_list) > 0

    def test_provinsi_structure(self) -> None:
        """Test that provinsi data has correct structure."""
        loader = get_loader()
        provinsi = loader.provinsi_list[0]

        assert "kode" in provinsi
        assert "nama" in provinsi
        assert "tingkat" in provinsi
        assert provinsi["tingkat"] == 1

    def test_provinsi_exists(self) -> None:
        """Test provinsi_exists method."""
        loader = get_loader()
        assert loader.provinsi_exists(11)  # Aceh exists
        assert not loader.provinsi_exists(999)  # Invalid code

    def test_kabupaten_by_provinsi(self) -> None:
        """Test kabupaten_by_provinsi method."""
        loader = get_loader()
        result = loader.kabupaten_by_provinsi(11)

        assert result is not None
        assert len(result) > 0
        assert all(item["provinsi"] == 11 for item in result)

    def test_kabupaten_by_provinsi_invalid(self) -> None:
        """Test kabupaten_by_provinsi with invalid code."""
        loader = get_loader()
        result = loader.kabupaten_by_provinsi(999)
        assert result is None

    def test_kabupaten_in_provinsi(self) -> None:
        """Test kabupaten_in_provinsi method."""
        loader = get_loader()
        assert loader.kabupaten_in_provinsi(1101, 11)  # Valid
        assert not loader.kabupaten_in_provinsi(1101, 12)  # Wrong provinsi
        assert not loader.kabupaten_in_provinsi(9999, 11)  # Invalid kabupaten

    def test_kecamatan_by_kabupaten(self) -> None:
        """Test kecamatan_by_kabupaten method."""
        loader = get_loader()
        result = loader.kecamatan_by_kabupaten(1101)

        assert result is not None
        assert isinstance(result, list)

    def test_kecamatan_in_kabupaten(self) -> None:
        """Test kecamatan_in_kabupaten method."""
        loader = get_loader()
        result = loader.kecamatan_by_kabupaten(1101)

        if result and len(result) > 0:
            kecamatan_code = result[0]["kode"]
            assert loader.kecamatan_in_kabupaten(kecamatan_code, 1101)

    def test_desa_by_kecamatan(self) -> None:
        """Test desa_by_kecamatan method."""
        loader = get_loader()
        result = loader.desa_by_kecamatan(110101)

        assert result is not None
        assert isinstance(result, list)

    def test_find_by_code_provinsi(self) -> None:
        """Test find_by_code method for provinsi."""
        loader = get_loader()
        result = loader.find_by_code(11)

        assert result is not None
        assert result["kode"] == 11
        assert result["tingkat"] == 1

    def test_find_by_code_kabupaten(self) -> None:
        """Test find_by_code method for kabupaten."""
        loader = get_loader()
        result = loader.find_by_code(1101)

        assert result is not None
        assert result["kode"] == 1101
        assert result["tingkat"] == 2
        assert "provinsi" in result

    def test_find_by_code_kecamatan(self) -> None:
        """Test find_by_code method for kecamatan."""
        loader = get_loader()
        result = loader.find_by_code(110101)

        assert result is not None
        assert result["kode"] == 110101
        assert result["tingkat"] == 3
        assert "kabupaten" in result

    def test_find_by_code_desa(self) -> None:
        """Test find_by_code method for desa - main requirement."""
        loader = get_loader()
        result = loader.find_by_code(1101012001)

        assert result is not None
        assert result["kode"] == 1101012001
        assert "nama" in result
        assert result["tingkat"] == 4
        assert "kecamatan" in result

    def test_find_by_code_not_found(self) -> None:
        """Test find_by_code method with invalid code."""
        loader = get_loader()
        result = loader.find_by_code(999999999)
        assert result is None

    def test_all_codes_indexed(self) -> None:
        """Test that all codes from all levels are indexed."""
        loader = get_loader()

        # Check that we can find codes from all levels
        provinsi_found = loader.find_by_code(11) is not None
        kabupaten_found = loader.find_by_code(1101) is not None
        kecamatan_found = loader.find_by_code(110101) is not None
        desa_found = loader.find_by_code(1101012001) is not None

        assert provinsi_found
        assert kabupaten_found
        assert kecamatan_found
        assert desa_found
