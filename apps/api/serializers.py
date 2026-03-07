from rest_framework import serializers

from apps.wilayah.models import Desa, Kabupaten, Kecamatan, Provinsi


class ProvinsiSerializer(serializers.ModelSerializer):
    jumlah_kabupaten = serializers.IntegerField(read_only=True)

    class Meta:
        model = Provinsi
        fields = ("kode", "nama", "tingkat", "jumlah_kabupaten")


class KabupatenSerializer(serializers.ModelSerializer):
    jumlah_kecamatan = serializers.IntegerField(read_only=True)
    provinsi_nama = serializers.CharField(source="provinsi.nama", read_only=True)

    class Meta:
        model = Kabupaten
        fields = ("kode", "nama", "tingkat", "provinsi_nama", "jumlah_kecamatan")


class KecamatanSerializer(serializers.ModelSerializer):
    jumlah_desa = serializers.IntegerField(read_only=True)
    kabupaten_nama = serializers.CharField(source="kabupaten.nama", read_only=True)

    class Meta:
        model = Kecamatan
        fields = ("kode", "nama", "tingkat", "kabupaten_nama", "jumlah_desa")


class DesaSerializer(serializers.ModelSerializer):
    kecamatan_nama = serializers.CharField(source="kecamatan.nama", read_only=True)

    class Meta:
        model = Desa
        fields = ("kode", "nama", "tingkat", "kecamatan_nama")
