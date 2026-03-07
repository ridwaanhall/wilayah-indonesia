import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.wilayah.models import Provinsi


class Command(BaseCommand):
    help = "Load province data from ppwp/0.json into the Provinsi table"

    def handle(self, *args, **options):
        json_path = Path(__file__).resolve().parents[4] / "ppwp" / "0.json"

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        created = 0
        updated = 0

        for item in data:
            _, is_created = Provinsi.objects.update_or_create(
                kode=int(item["kode"]),
                defaults={
                    "nama": item["nama"],
                    "tingkat": item["tingkat"],
                },
            )
            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, Updated: {updated}, Total: {created + updated}"
            )
        )
