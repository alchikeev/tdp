#!/usr/bin/env python3
"""Export key models to JSON with all fields, including slugs and foreign keys."""
import json
import os
import sys
from pathlib import Path

import django


# Ensure project root is on PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def main() -> None:
    # Configure settings and initialise Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
    django.setup()

    from tours.models import TourCategory, Tour
    from blog.models import BlogPost
    from news.models import NewsPost
    from reviews.models import Review
    from django.core import serializers

    data = {}
    querysets = {
        "tour_categories": TourCategory.objects.all(),
        "tours": Tour.objects.all(),
        "blog_posts": BlogPost.objects.all(),
        "news_posts": NewsPost.objects.all(),
        "reviews": Review.objects.all(),
    }

    for key, queryset in querysets.items():
        # ``serializers.serialize`` includes M2M relations and foreign keys
        data[key] = json.loads(
            serializers.serialize(
                "json",
                queryset,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True,
            )
        )

    backup_dir = BASE_DIR / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    output_file = backup_dir / "full_backup.json"
    with output_file.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    print(f"Backup saved to {output_file}")


if __name__ == "__main__":
    main()
