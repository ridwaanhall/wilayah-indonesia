from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from apps.wilayah.models import Desa, Kabupaten, Kecamatan, Provinsi

from .serializers import (
    DesaSerializer,
    KabupatenSerializer,
    KecamatanSerializer,
    ProvinsiSerializer,
)


class APIRootView(APIView):
    """Root endpoint showing available API resources."""

    def get(self, request, *args, **kwargs):
        return Response({
            "provinsi": reverse("api:provinsi-list", request=request),
        })


class ProvinsiListView(ListAPIView):
    """List all provinces with kabupaten count."""

    serializer_class = ProvinsiSerializer

    def get_queryset(self):
        return (
            Provinsi.objects
            .annotate(jumlah_kabupaten=Count("kabupaten"))
            .order_by("kode")
        )


class KabupatenListView(ListAPIView):
    """List kabupaten/kota within a province."""

    serializer_class = KabupatenSerializer

    def get_queryset(self):
        kode_provinsi = self.kwargs["kode_provinsi"]
        get_object_or_404(Provinsi, kode=kode_provinsi)
        return (
            Kabupaten.objects
            .filter(provinsi__kode=kode_provinsi)
            .select_related("provinsi")
            .annotate(jumlah_kecamatan=Count("kecamatan"))
            .order_by("kode")
        )


class KecamatanListView(ListAPIView):
    """List kecamatan within a kabupaten."""

    serializer_class = KecamatanSerializer

    def get_queryset(self):
        kode_kabupaten = self.kwargs["kode_kabupaten"]
        get_object_or_404(Kabupaten, kode=kode_kabupaten)
        return (
            Kecamatan.objects
            .filter(kabupaten__kode=kode_kabupaten)
            .select_related("kabupaten")
            .annotate(jumlah_desa=Count("desa"))
            .order_by("kode")
        )


class DesaListView(ListAPIView):
    """List desa/kelurahan within a kecamatan."""

    serializer_class = DesaSerializer

    def get_queryset(self):
        kode_kecamatan = self.kwargs["kode_kecamatan"]
        get_object_or_404(Kecamatan, kode=kode_kecamatan)
        return (
            Desa.objects
            .filter(kecamatan__kode=kode_kecamatan)
            .select_related("kecamatan")
            .order_by("kode")
        )
