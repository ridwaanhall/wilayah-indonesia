from django.db import models

class Provinsi(models.Model):
    id = models.BigAutoField(primary_key=True)
    kode = models.PositiveIntegerField(unique=True)
    nama = models.CharField(max_length=100)
    tingkat = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = "provinsi"
        verbose_name_plural = "Provinsi"
        ordering = ["kode"]

    def __str__(self):
        return f"{self.kode} - {self.nama}"


class Kabupaten(models.Model):
    id = models.BigAutoField(primary_key=True)
    kode = models.PositiveIntegerField(unique=True)
    nama = models.CharField(max_length=100)
    provinsi = models.ForeignKey(Provinsi, on_delete=models.CASCADE, related_name="kabupaten")
    tingkat = models.PositiveSmallIntegerField(default=2)

    class Meta:
        db_table = "kabupaten"
        verbose_name_plural = "Kabupaten"
        ordering = ["kode"]

    def __str__(self):
        return f"{self.kode} - {self.nama}"


class Kecamatan(models.Model):
    id = models.BigAutoField(primary_key=True)
    kode = models.PositiveIntegerField(unique=True)
    nama = models.CharField(max_length=100)
    kabupaten = models.ForeignKey(Kabupaten, on_delete=models.CASCADE, related_name="kecamatan")
    tingkat = models.PositiveSmallIntegerField(default=3)

    class Meta:
        db_table = "kecamatan"
        verbose_name_plural = "Kecamatan"
        ordering = ["kode"]

    def __str__(self):
        return f"{self.kode} - {self.nama}"


class Desa(models.Model):
    id = models.BigAutoField(primary_key=True)
    kode = models.PositiveIntegerField(unique=True)
    nama = models.CharField(max_length=100)
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.CASCADE, related_name="desa")
    tingkat = models.PositiveSmallIntegerField(default=4)

    class Meta:
        db_table = "desa"
        verbose_name_plural = "Desa"
        ordering = ["kode"]

    def __str__(self):
        return f"{self.kode} - {self.nama}"
