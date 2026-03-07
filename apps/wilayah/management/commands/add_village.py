import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.wilayah.models import Kecamatan, Desa


class Command(BaseCommand):
    help = "Load village data from ppwp/<provinsi>/<kabupaten>/<kecamatan>.json into the Desa table"

    def handle(self, *args, **options):
        ppwp_dir = Path(__file__).resolve().parents[4] / "ppwp"

        created = 0
        updated = 0

        for provinsi_dir in sorted(ppwp_dir.iterdir()):
            if not provinsi_dir.is_dir():
                continue

            for kabupaten_dir in sorted(provinsi_dir.iterdir()):
                if not kabupaten_dir.is_dir():
                    continue

                for json_file in sorted(kabupaten_dir.glob("*.json")):
                    kode_kecamatan = int(json_file.stem)
                    try:
                        kecamatan = Kecamatan.objects.get(kode=kode_kecamatan)
                    except Kecamatan.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f"Kecamatan {kode_kecamatan} not found, skipping {json_file}")
                        )
                        continue

                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    for item in data:
                        _, is_created = Desa.objects.update_or_create(
                            kode=int(item["kode"]),
                            defaults={
                                "nama": item["nama"],
                                "kecamatan": kecamatan,
                                "tingkat": item["tingkat"],
                            },
                        )
                        if is_created:
                            created += 1
                        else:
                            updated += 1

                self.stdout.write(f"Processed {provinsi_dir.name}/{kabupaten_dir.name}/")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, Updated: {updated}, Total: {created + updated}"
            )
        )
