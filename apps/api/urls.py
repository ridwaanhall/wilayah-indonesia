from django.urls import path

from . import views

app_name = "api"

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
