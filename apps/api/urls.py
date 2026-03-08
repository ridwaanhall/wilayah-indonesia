from django.conf import settings
from django.urls import path

from . import views

app_name = "api"

if settings.DEBUG:
    urlpatterns = [
        path(
            "",
            views.APIRootView.as_view(),
            name="api-root",
        ),
        path(
            "0/",
            views.ProvinsiListView.as_view(),
            name="provinsi-list",
        ),
        path(
            "<int:kode_provinsi>/",
            views.KabupatenListView.as_view(),
            name="kabupaten-list",
        ),
        path(
            "<int:kode_provinsi>/<int:kode_kabupaten>/",
            views.KecamatanListView.as_view(),
            name="kecamatan-list",
        ),
        path(
            "<int:kode_provinsi>/<int:kode_kabupaten>/<int:kode_kecamatan>/",
            views.DesaListView.as_view(),
            name="desa-list",
        ),
    ]
else:
    urlpatterns = [
        path(
            "",
            views.APIRootView.as_view(),
            name="api-root",
        ),
        path(
            "0/",
            views.JSONProvinsiListView.as_view(),
            name="provinsi-list",
        ),
        path(
            "<int:kode_provinsi>/",
            views.JSONKabupatenListView.as_view(),
            name="kabupaten-list",
        ),
        path(
            "<int:kode_provinsi>/<int:kode_kabupaten>/",
            views.JSONKecamatanListView.as_view(),
            name="kecamatan-list",
        ),
        path(
            "<int:kode_provinsi>/<int:kode_kabupaten>/<int:kode_kecamatan>/",
            views.JSONDesaListView.as_view(),
            name="desa-list",
        ),
    ]
