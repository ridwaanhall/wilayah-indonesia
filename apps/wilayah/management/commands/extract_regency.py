import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.wilayah.models import Kabupaten


class Command(BaseCommand):
    help = "Extract all Kabupaten data from database to apps/wilayah/data/kabupaten.json"

    def handle(self, *args, **options):
        data_dir = Path(__file__).resolve().parents[2] / "data"
        data_dir.mkdir(exist_ok=True)

        kabupaten_list = list(
            Kabupaten.objects
            .order_by("kode")
            .values("kode", "nama", "provinsi_id", "tingkat")
        )

        # Rename provinsi_id to provinsi for cleaner JSON
        for item in kabupaten_list:
            item["provinsi"] = item.pop("provinsi_id")

        output_path = data_dir / "kabupaten.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(kabupaten_list, f, ensure_ascii=False, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f"Extracted {len(kabupaten_list)} kabupaten to {output_path}")
        )
