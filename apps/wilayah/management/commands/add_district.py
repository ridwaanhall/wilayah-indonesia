import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.wilayah.models import Kabupaten, Kecamatan


class Command(BaseCommand):
    help = "Load district data from ppwp/<provinsi>/<kabupaten>.json into the Kecamatan table"

    def handle(self, *args, **options):
        ppwp_dir = Path(__file__).resolve().parents[4] / "ppwp"

        created = 0
        updated = 0

        for provinsi_dir in sorted(ppwp_dir.iterdir()):
            if not provinsi_dir.is_dir():
                continue

            for json_file in sorted(provinsi_dir.glob("*.json")):
                kode_kabupaten = int(json_file.stem)
                try:
                    kabupaten = Kabupaten.objects.get(kode=kode_kabupaten)
                except Kabupaten.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"Kabupaten {kode_kabupaten} not found, skipping {json_file}")
                    )
                    continue

                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for item in data:
                    _, is_created = Kecamatan.objects.update_or_create(
                        kode=int(item["kode"]),
                        defaults={
                            "nama": item["nama"],
                            "kabupaten": kabupaten,
                            "tingkat": item["tingkat"],
                        },
                    )
                    if is_created:
                        created += 1
                    else:
                        updated += 1

            self.stdout.write(f"Processed {provinsi_dir.name}/")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, Updated: {updated}, Total: {created + updated}"
            )
        )
