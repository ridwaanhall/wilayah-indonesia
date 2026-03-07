from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Desa, Kabupaten, Kecamatan, Provinsi


class KabupatenInline(admin.TabularInline):
    model = Kabupaten
    fields = ("kode", "nama", "tingkat")
    extra = 0
    show_change_link = True
    ordering = ("kode",)


class KecamatanInline(admin.TabularInline):
    model = Kecamatan
    fields = ("kode", "nama", "tingkat")
    extra = 0
    show_change_link = True
    ordering = ("kode",)


class DesaInline(admin.TabularInline):
    model = Desa
    fields = ("kode", "nama", "tingkat")
    extra = 0
    show_change_link = True
    ordering = ("kode",)


@admin.register(Provinsi)
class ProvinsiAdmin(admin.ModelAdmin):
    list_display = ("kode", "nama", "tingkat", "jumlah_kabupaten")
    list_display_links = ("kode", "nama")
    search_fields = ("kode", "nama")
    list_filter = ("tingkat",)
    list_per_page = 40
    ordering = ("kode",)
    inlines = (KabupatenInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_jumlah_kabupaten=Count("kabupaten"))

    @admin.display(description="Jumlah Kabupaten/Kota", ordering="_jumlah_kabupaten")
    def jumlah_kabupaten(self, obj):
        return obj._jumlah_kabupaten


@admin.register(Kabupaten)
class KabupatenAdmin(admin.ModelAdmin):
    list_display = ("kode", "nama", "provinsi_link", "tingkat", "jumlah_kecamatan")
    list_display_links = ("kode", "nama")
    search_fields = ("kode", "nama", "provinsi__nama")
    list_filter = ("tingkat", "provinsi")
    list_per_page = 50
    ordering = ("kode",)
    list_select_related = ("provinsi",)
    autocomplete_fields = ("provinsi",)
    inlines = (KecamatanInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_jumlah_kecamatan=Count("kecamatan"))

    @admin.display(description="Provinsi", ordering="provinsi__nama")
    def provinsi_link(self, obj):
        return format_html(
            '<a href="/admin/wilayah/provinsi/{}/change/">{}</a>',
            obj.provinsi_id,
            obj.provinsi,
        )

    @admin.display(description="Jumlah Kecamatan", ordering="_jumlah_kecamatan")
    def jumlah_kecamatan(self, obj):
        return obj._jumlah_kecamatan


@admin.register(Kecamatan)
class KecamatanAdmin(admin.ModelAdmin):
    list_display = ("kode", "nama", "kabupaten_link", "tingkat", "jumlah_desa")
    list_display_links = ("kode", "nama")
    search_fields = ("kode", "nama", "kabupaten__nama", "kabupaten__provinsi__nama")
    list_filter = ("tingkat", "kabupaten__provinsi")
    list_per_page = 50
    ordering = ("kode",)
    list_select_related = ("kabupaten", "kabupaten__provinsi")
    autocomplete_fields = ("kabupaten",)
    inlines = (DesaInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_jumlah_desa=Count("desa"))

    @admin.display(description="Kabupaten/Kota", ordering="kabupaten__nama")
    def kabupaten_link(self, obj):
        return format_html(
            '<a href="/admin/wilayah/kabupaten/{}/change/">{}</a>',
            obj.kabupaten_id,
            obj.kabupaten,
        )

    @admin.display(description="Jumlah Desa/Kelurahan", ordering="_jumlah_desa")
    def jumlah_desa(self, obj):
        return obj._jumlah_desa


@admin.register(Desa)
class DesaAdmin(admin.ModelAdmin):
    list_display = ("kode", "nama", "kecamatan_link", "kabupaten_display", "tingkat")
    list_display_links = ("kode", "nama")
    search_fields = ("kode", "nama", "kecamatan__nama", "kecamatan__kabupaten__nama")
    list_filter = ("tingkat", "kecamatan__kabupaten__provinsi")
    list_per_page = 50
    ordering = ("kode",)
    list_select_related = ("kecamatan", "kecamatan__kabupaten", "kecamatan__kabupaten__provinsi")
    autocomplete_fields = ("kecamatan",)

    @admin.display(description="Kecamatan", ordering="kecamatan__nama")
    def kecamatan_link(self, obj):
        return format_html(
            '<a href="/admin/wilayah/kecamatan/{}/change/">{}</a>',
            obj.kecamatan_id,
            obj.kecamatan,
        )

    @admin.display(description="Kabupaten/Kota", ordering="kecamatan__kabupaten__nama")
    def kabupaten_display(self, obj):
        return obj.kecamatan.kabupaten
