from rest_framework import serializers

from apps.wilayah.models import Desa, Kabupaten, Kecamatan, Provinsi


# ── Simple serializers (default) ──────────────────────────────────────────────

class ProvinsiSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provinsi
        fields = ("kode", "nama", "tingkat")


class KabupatenSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kabupaten
        fields = ("kode", "nama", "tingkat")


class KecamatanSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kecamatan
        fields = ("kode", "nama", "tingkat")


class DesaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desa
        fields = ("kode", "nama", "tingkat")


# ── Advanced serializers ──────────────────────────────────────────────────────

class ProvinsiAdvancedSerializer(serializers.ModelSerializer):
    jumlah_kabupaten = serializers.IntegerField(read_only=True)

    class Meta:
        model = Provinsi
        fields = ("kode", "nama", "tingkat", "jumlah_kabupaten")


class KabupatenAdvancedSerializer(serializers.ModelSerializer):
    jumlah_kecamatan = serializers.IntegerField(read_only=True)
    provinsi_nama = serializers.CharField(source="provinsi.nama", read_only=True)

    class Meta:
        model = Kabupaten
        fields = ("kode", "nama", "tingkat", "provinsi_nama", "jumlah_kecamatan")


class KecamatanAdvancedSerializer(serializers.ModelSerializer):
    jumlah_desa = serializers.IntegerField(read_only=True)
    kabupaten_nama = serializers.CharField(source="kabupaten.nama", read_only=True)

    class Meta:
        model = Kecamatan
        fields = ("kode", "nama", "tingkat", "kabupaten_nama", "jumlah_desa")


class DesaAdvancedSerializer(serializers.ModelSerializer):
    kecamatan_nama = serializers.CharField(source="kecamatan.nama", read_only=True)

    class Meta:
        model = Desa
        fields = ("kode", "nama", "tingkat", "kecamatan_nama")
