from django.conf import settings
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from apps.wilayah.models import Desa, Kabupaten, Kecamatan, Provinsi

from .serializers import (
    DesaAdvancedSerializer,
    DesaSimpleSerializer,
    KabupatenAdvancedSerializer,
    KabupatenSimpleSerializer,
    KecamatanAdvancedSerializer,
    KecamatanSimpleSerializer,
    ProvinsiAdvancedSerializer,
    ProvinsiSimpleSerializer,
)


def is_advanced():
    return getattr(settings, "API_ADVANCED_MODE", False)


def is_debug():
    return getattr(settings, "DEBUG", False)


class WilayahPagination(PageNumberPagination):
    def get_page_size(self, request):
        return getattr(settings, 'REST_FRAMEWORK', {}).get('PAGE_SIZE', 100)


class APIRootView(APIView):
    """Root endpoint showing available API resources."""

    def get(self, request, *args, **kwargs):
        return Response({
            "list-provinsi": reverse("api:provinsi-list", request=request),
        })


# ── Production JSON views (DEBUG=False) ──────────────────────────────────────

class JSONProvinsiListView(APIView):
    def get(self, request, *args, **kwargs):
        from apps.wilayah.loader import get_provinsi_list
        return Response(get_provinsi_list())


class JSONKabupatenListView(APIView):
    def get(self, request, *args, **kwargs):
        from apps.wilayah.loader import get_kabupaten_by_provinsi, provinsi_exists
        kode_provinsi = self.kwargs["kode_provinsi"]
        if not provinsi_exists(kode_provinsi):
            raise Http404
        return Response(get_kabupaten_by_provinsi(kode_provinsi))


class JSONKecamatanListView(APIView):
    def get(self, request, *args, **kwargs):
        from apps.wilayah.loader import get_kecamatan_by_kabupaten, kabupaten_exists
        kode_kabupaten = self.kwargs["kode_kabupaten"]
        if not kabupaten_exists(kode_kabupaten):
            raise Http404
        return Response(get_kecamatan_by_kabupaten(kode_kabupaten))


class JSONDesaListView(APIView):
    def get(self, request, *args, **kwargs):
        from apps.wilayah.loader import get_desa_by_kecamatan, kecamatan_exists
        kode_kecamatan = self.kwargs["kode_kecamatan"]
        if not kecamatan_exists(kode_kecamatan):
            raise Http404
        return Response(get_desa_by_kecamatan(kode_kecamatan))


# ── Development DB views (DEBUG=True) ────────────────────────────────────────

class ProvinsiListView(ListAPIView):
    """List all provinces."""

    @property
    def pagination_class(self):
        return WilayahPagination if is_advanced() else None

    def get_serializer_class(self):
        return ProvinsiAdvancedSerializer if is_advanced() else ProvinsiSimpleSerializer

    def get_queryset(self):
        qs = Provinsi.objects.order_by("kode")
        if is_advanced():
            qs = qs.annotate(jumlah_kabupaten=Count("kabupaten"))
        return qs


class KabupatenListView(ListAPIView):
    """List kabupaten/kota within a province."""

    @property
    def pagination_class(self):
        return WilayahPagination if is_advanced() else None

    def get_serializer_class(self):
        return KabupatenAdvancedSerializer if is_advanced() else KabupatenSimpleSerializer

    def get_queryset(self):
        kode_provinsi = self.kwargs["kode_provinsi"]
        get_object_or_404(Provinsi, kode=kode_provinsi)
        qs = Kabupaten.objects.filter(provinsi__kode=kode_provinsi).order_by("kode")
        if is_advanced():
            qs = qs.select_related("provinsi").annotate(jumlah_kecamatan=Count("kecamatan"))
        return qs


class KecamatanListView(ListAPIView):
    """List kecamatan within a kabupaten."""

    @property
    def pagination_class(self):
        return WilayahPagination if is_advanced() else None

    def get_serializer_class(self):
        return KecamatanAdvancedSerializer if is_advanced() else KecamatanSimpleSerializer

    def get_queryset(self):
        kode_kabupaten = self.kwargs["kode_kabupaten"]
        get_object_or_404(Kabupaten, kode=kode_kabupaten)
        qs = Kecamatan.objects.filter(kabupaten__kode=kode_kabupaten).order_by("kode")
        if is_advanced():
            qs = qs.select_related("kabupaten").annotate(jumlah_desa=Count("desa"))
        return qs


class DesaListView(ListAPIView):
    """List desa/kelurahan within a kecamatan."""

    @property
    def pagination_class(self):
        return WilayahPagination if is_advanced() else None

    def get_serializer_class(self):
        return DesaAdvancedSerializer if is_advanced() else DesaSimpleSerializer

    def get_queryset(self):
        kode_kecamatan = self.kwargs["kode_kecamatan"]
        get_object_or_404(Kecamatan, kode=kode_kecamatan)
        qs = Desa.objects.filter(kecamatan__kode=kode_kecamatan).order_by("kode")
        if is_advanced():
            qs = qs.select_related("kecamatan")
        return qs
