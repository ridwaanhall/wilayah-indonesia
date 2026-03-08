import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.wilayah.models import Kecamatan


class Command(BaseCommand):
    help = "Extract all Kecamatan data from database to apps/wilayah/data/kecamatan.json"

    def handle(self, *args, **options):
        data_dir = Path(__file__).resolve().parents[2] / "data"
        data_dir.mkdir(exist_ok=True)

        kecamatan_list = list(
            Kecamatan.objects
            .order_by("kode")
            .values("kode", "nama", "kabupaten_id", "tingkat")
        )

        for item in kecamatan_list:
            item["kabupaten"] = item.pop("kabupaten_id")

        output_path = data_dir / "kecamatan.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(kecamatan_list, f, ensure_ascii=False, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f"Extracted {len(kecamatan_list)} kecamatan to {output_path}")
        )
