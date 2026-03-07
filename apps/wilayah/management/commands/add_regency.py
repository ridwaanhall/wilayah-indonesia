import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.wilayah.models import Kabupaten, Provinsi


class Command(BaseCommand):
    help = "Load regency data from ppwp/<kode_provinsi>.json into the Kabupaten table"

    def handle(self, *args, **options):
        ppwp_dir = Path(__file__).resolve().parents[4] / "ppwp"
        exclude = {"0.json", "99.json"}

        created = 0
        updated = 0

        for json_file in sorted(ppwp_dir.glob("*.json")):
            if json_file.name in exclude:
                continue

            kode_provinsi = int(json_file.stem)
            try:
                provinsi = Provinsi.objects.get(kode=kode_provinsi)
            except Provinsi.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Provinsi {kode_provinsi} not found, skipping {json_file.name}")
                )
                continue

            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                _, is_created = Kabupaten.objects.update_or_create(
                    kode=int(item["kode"]),
                    defaults={
                        "nama": item["nama"],
                        "provinsi": provinsi,
                        "tingkat": item["tingkat"],
                    },
                )
                if is_created:
                    created += 1
                else:
                    updated += 1

            self.stdout.write(f"Processed {json_file.name} ({len(data)} records)")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, Updated: {updated}, Total: {created + updated}"
            )
        )
