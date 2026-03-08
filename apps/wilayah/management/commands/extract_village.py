import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.wilayah.models import Desa


class Command(BaseCommand):
    help = "Extract all Desa data from database to apps/wilayah/data/desa.json"

    def handle(self, *args, **options):
        data_dir = Path(__file__).resolve().parents[2] / "data"
        data_dir.mkdir(exist_ok=True)

        desa_list = list(
            Desa.objects
            .order_by("kode")
            .values("kode", "nama", "kecamatan_id", "tingkat")
        )

        for item in desa_list:
            item["kecamatan"] = item.pop("kecamatan_id")

        output_path = data_dir / "desa.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(desa_list, f, ensure_ascii=False, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f"Extracted {len(desa_list)} desa to {output_path}")
        )
