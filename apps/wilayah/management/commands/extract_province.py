import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.wilayah.models import Provinsi


class Command(BaseCommand):
    help = "Extract all Provinsi data from database to apps/wilayah/data/provinsi.json"

    def handle(self, *args, **options):
        data_dir = Path(__file__).resolve().parents[2] / "data"
        data_dir.mkdir(exist_ok=True)

        provinsi_list = list(
            Provinsi.objects.order_by("kode").values("kode", "nama", "tingkat")
        )

        output_path = data_dir / "provinsi.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(provinsi_list, f, ensure_ascii=False, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f"Extracted {len(provinsi_list)} provinsi to {output_path}")
        )
