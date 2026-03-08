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


def _build_url(request, view_name, kwargs=None):
    return reverse(view_name, kwargs=kwargs, request=request)


class APIRootView(APIView):
    """Endpoint utama yang menampilkan daftar sumber data API."""

    def get(self, request, *args, **kwargs):
        return Response({
            "daftar-provinsi": reverse("api:provinsi-list", request=request),
        })

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["page_title"] = "Beranda"
        request = context.get("request")
        context["breadcrumbs"] = [
            ("INDONESIA", _build_url(request, "api:api-root")),
        ]
        return context


# ── Production JSON views (DEBUG=False) ──────────────────────────────────────

class JSONProvinsiListView(APIView):
    """Daftar seluruh provinsi di Indonesia."""

    def get(self, request, *args, **kwargs):
        from apps.wilayah.loader import get_provinsi_list
        return Response(get_provinsi_list())

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["page_title"] = "Daftar Provinsi"
        request = context.get("request")
        context["breadcrumbs"] = [
            ("INDONESIA", _build_url(request, "api:api-root")),
            ("Daftar Provinsi", _build_url(request, "api:provinsi-list")),
        ]
        return context


class JSONKabupatenListView(APIView):
    """Daftar kabupaten/kota dalam suatu provinsi."""

    def get(self, request, *args, **kwargs):
        from apps.wilayah.loader import get_kabupaten_by_provinsi, provinsi_exists
        kode_provinsi = self.kwargs["kode_provinsi"]
        if not provinsi_exists(kode_provinsi):
            raise Http404
        return Response(get_kabupaten_by_provinsi(kode_provinsi))

    def get_renderer_context(self):
        context = super().get_renderer_context()
        from apps.wilayah.loader import get_provinsi_nama
        kode_provinsi = self.kwargs["kode_provinsi"]
        nama_provinsi = get_provinsi_nama(kode_provinsi)
        context["page_title"] = f"Daftar Kabupaten/Kota di {nama_provinsi}"
        request = context.get("request")
        context["breadcrumbs"] = [
            ("INDONESIA", _build_url(request, "api:api-root")),
            (nama_provinsi, _build_url(request, "api:kabupaten-list", {"kode_provinsi": kode_provinsi})),
        ]
        return context


class JSONKecamatanListView(APIView):
    """Daftar kecamatan dalam suatu kabupaten/kota."""

    def get(self, request, *args, **kwargs):
        from apps.wilayah.loader import get_kecamatan_by_kabupaten, kabupaten_exists
        kode_kabupaten = self.kwargs["kode_kabupaten"]
        if not kabupaten_exists(kode_kabupaten):
            raise Http404
        return Response(get_kecamatan_by_kabupaten(kode_kabupaten))

    def get_renderer_context(self):
        context = super().get_renderer_context()
        from apps.wilayah.loader import get_kabupaten_nama, get_provinsi_nama
        kode_provinsi = self.kwargs["kode_provinsi"]
        kode_kabupaten = self.kwargs["kode_kabupaten"]
        nama_provinsi = get_provinsi_nama(kode_provinsi)
        nama_kabupaten = get_kabupaten_nama(kode_kabupaten)
        context["page_title"] = f"Daftar Kecamatan di {nama_kabupaten}, {nama_provinsi}"
        request = context.get("request")
        context["breadcrumbs"] = [
            ("INDONESIA", _build_url(request, "api:api-root")),
            (nama_provinsi, _build_url(request, "api:kabupaten-list", {"kode_provinsi": kode_provinsi})),
            (nama_kabupaten, _build_url(request, "api:kecamatan-list", {"kode_provinsi": kode_provinsi, "kode_kabupaten": kode_kabupaten})),
        ]
        return context


class JSONDesaListView(APIView):
    """Daftar desa/kelurahan dalam suatu kecamatan."""

    def get(self, request, *args, **kwargs):
        from apps.wilayah.loader import get_desa_by_kecamatan, kecamatan_exists
        kode_kecamatan = self.kwargs["kode_kecamatan"]
        if not kecamatan_exists(kode_kecamatan):
            raise Http404
        return Response(get_desa_by_kecamatan(kode_kecamatan))

    def get_renderer_context(self):
        context = super().get_renderer_context()
        from apps.wilayah.loader import get_kabupaten_nama, get_kecamatan_nama, get_provinsi_nama
        kode_provinsi = self.kwargs["kode_provinsi"]
        kode_kabupaten = self.kwargs["kode_kabupaten"]
        kode_kecamatan = self.kwargs["kode_kecamatan"]
        nama_provinsi = get_provinsi_nama(kode_provinsi)
        nama_kabupaten = get_kabupaten_nama(kode_kabupaten)
        nama_kecamatan = get_kecamatan_nama(kode_kecamatan)
        context["page_title"] = f"Daftar Desa/Kelurahan di {nama_kecamatan}, {nama_kabupaten}, {nama_provinsi}"
        request = context.get("request")
        context["breadcrumbs"] = [
            ("INDONESIA", _build_url(request, "api:api-root")),
            (nama_provinsi, _build_url(request, "api:kabupaten-list", {"kode_provinsi": kode_provinsi})),
            (nama_kabupaten, _build_url(request, "api:kecamatan-list", {"kode_provinsi": kode_provinsi, "kode_kabupaten": kode_kabupaten})),
            (nama_kecamatan, _build_url(request, "api:desa-list", {"kode_provinsi": kode_provinsi, "kode_kabupaten": kode_kabupaten, "kode_kecamatan": kode_kecamatan})),
        ]
        return context


# ── Development DB views (DEBUG=True) ────────────────────────────────────────

class ProvinsiListView(ListAPIView):
    """Daftar seluruh provinsi di Indonesia."""

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

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["page_title"] = "Daftar Provinsi"
        request = context.get("request")
        context["breadcrumbs"] = [
            ("INDONESIA", _build_url(request, "api:api-root")),
            ("Daftar Provinsi", _build_url(request, "api:provinsi-list")),
        ]
        return context


class KabupatenListView(ListAPIView):
    """Daftar kabupaten/kota dalam suatu provinsi."""

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

    def get_renderer_context(self):
        context = super().get_renderer_context()
        kode_provinsi = self.kwargs["kode_provinsi"]
        nama_provinsi = Provinsi.objects.filter(kode=kode_provinsi).values_list("nama", flat=True).first() or ""
        context["page_title"] = f"Daftar Kabupaten/Kota di {nama_provinsi}"
        request = context.get("request")
        context["breadcrumbs"] = [
            ("INDONESIA", _build_url(request, "api:api-root")),
            (nama_provinsi, _build_url(request, "api:kabupaten-list", {"kode_provinsi": kode_provinsi})),
        ]
        return context


class KecamatanListView(ListAPIView):
    """Daftar kecamatan dalam suatu kabupaten/kota."""

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

    def get_renderer_context(self):
        context = super().get_renderer_context()
        kode_provinsi = self.kwargs["kode_provinsi"]
        kode_kabupaten = self.kwargs["kode_kabupaten"]
        nama_provinsi = Provinsi.objects.filter(kode=kode_provinsi).values_list("nama", flat=True).first() or ""
        nama_kabupaten = Kabupaten.objects.filter(kode=kode_kabupaten).values_list("nama", flat=True).first() or ""
        context["page_title"] = f"Daftar Kecamatan di {nama_kabupaten}, {nama_provinsi}"
        request = context.get("request")
        context["breadcrumbs"] = [
            ("INDONESIA", _build_url(request, "api:api-root")),
            (nama_provinsi, _build_url(request, "api:kabupaten-list", {"kode_provinsi": kode_provinsi})),
            (nama_kabupaten, _build_url(request, "api:kecamatan-list", {"kode_provinsi": kode_provinsi, "kode_kabupaten": kode_kabupaten})),
        ]
        return context


class DesaListView(ListAPIView):
    """Daftar desa/kelurahan dalam suatu kecamatan."""

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

    def get_renderer_context(self):
        context = super().get_renderer_context()
        kode_provinsi = self.kwargs["kode_provinsi"]
        kode_kabupaten = self.kwargs["kode_kabupaten"]
        kode_kecamatan = self.kwargs["kode_kecamatan"]
        nama_provinsi = Provinsi.objects.filter(kode=kode_provinsi).values_list("nama", flat=True).first() or ""
        nama_kabupaten = Kabupaten.objects.filter(kode=kode_kabupaten).values_list("nama", flat=True).first() or ""
        nama_kecamatan = Kecamatan.objects.filter(kode=kode_kecamatan).values_list("nama", flat=True).first() or ""
        context["page_title"] = f"Daftar Desa/Kelurahan di {nama_kecamatan}, {nama_kabupaten}, {nama_provinsi}"
        request = context.get("request")
        context["breadcrumbs"] = [
            ("INDONESIA", _build_url(request, "api:api-root")),
            (nama_provinsi, _build_url(request, "api:kabupaten-list", {"kode_provinsi": kode_provinsi})),
            (nama_kabupaten, _build_url(request, "api:kecamatan-list", {"kode_provinsi": kode_provinsi, "kode_kabupaten": kode_kabupaten})),
            (nama_kecamatan, _build_url(request, "api:desa-list", {"kode_provinsi": kode_provinsi, "kode_kabupaten": kode_kabupaten, "kode_kecamatan": kode_kecamatan})),
        ]
        return context
