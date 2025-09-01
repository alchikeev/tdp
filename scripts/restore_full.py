#!/usr/bin/env python
"""Restore full database from JSON dump.

This script expects a JSON file with keys for each model. Relationships
should be represented by slugs so that we can rebuild them after clearing the
database. Example structure::

{
  "categories": [{"name": "...","slug": "...","parent": null}],
  "tags": [{"name": "...","slug": "..."}],
  "tour_categories": [{"name": "...","slug": "...","parent": null}],
  "tours": [{
      "title": "...",
      "slug": "...",
      "category": "tour-category-slug",
      "tags": ["tag-slug"],
      "description": "...",
      "price_adult": "100.00"
  }],
  "service_categories": [...],
  "services": [...],
  "news": [...],
  "blog": [...],
  "reviews": [...],
  "prices": [...]
}

The script truncates existing data and recreates objects inside a single
transaction. Run it with::

    python scripts/restore_full.py path/to/full_backup.json

If the path is omitted, ``full_backup.json`` in the current working directory
is used.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from typing import Dict, Iterable, List

import django
from django.db import connection, transaction

DEFAULT_SETTINGS = "config.settings.dev"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS)

django.setup()

from core.models import Category, Tag
from tours.models import TourCategory, Tour
from services.models import ServiceCategory, Service
from news.models import NewsPost
from blog.models import BlogPost
from reviews.models import Review
from prices.models import PricePDF


def truncate_models(models: Iterable[type]) -> None:
    with connection.cursor() as cursor:
        if connection.vendor == "postgresql":
            tables = ", ".join(f'"{m._meta.db_table}"' for m in models)
            cursor.execute(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE")
        else:
            for m in models:
                m.objects.all().delete()


def create_categories(data: List[Dict], model) -> None:
    cache = {}
    for item in data:
        parent_slug = item.get("parent")
        fields = {k: v for k, v in item.items() if k != "parent"}
        obj = model.objects.create(**fields)
        cache[obj.slug] = (obj, parent_slug)
    for obj, parent_slug in cache.values():
        if parent_slug:
            obj.parent = model.objects.get(slug=parent_slug)
            obj.save(update_fields=["parent"])


def restore_from_dump(payload: Dict) -> None:
    create_categories(payload.get("categories", []), Category)
    for item in payload.get("tags", []):
        Tag.objects.create(**item)

    create_categories(payload.get("tour_categories", []), TourCategory)
    for item in payload.get("tours", []):
        category_slug = item.pop("category")
        tag_slugs = item.pop("tags", [])
        category = TourCategory.objects.get(slug=category_slug)
        tour = Tour.objects.create(category=category, **item)
        if tag_slugs:
            tags = list(Tag.objects.filter(slug__in=tag_slugs))
            tour.tags.set(tags)

    create_categories(payload.get("service_categories", []), ServiceCategory)
    for item in payload.get("services", []):
        category_slug = item.pop("category")
        tag_slugs = item.pop("tags", [])
        category = ServiceCategory.objects.get(slug=category_slug)
        service = Service.objects.create(category=category, **item)
        if tag_slugs:
            tags = list(Tag.objects.filter(slug__in=tag_slugs))
            service.tags.set(tags)

    for item in payload.get("news", []):
        NewsPost.objects.create(**item)
    for item in payload.get("blog", []):
        BlogPost.objects.create(**item)
    for item in payload.get("reviews", []):
        Review.objects.create(**item)
    for item in payload.get("prices", []):
        PricePDF.objects.create(**item)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dump",
        nargs="?",
        default="full_backup.json",
        help="Path to JSON dump file",
    )
    args = parser.parse_args(argv)

    if not os.path.exists(args.dump):
        parser.error(f"Dump file not found: {args.dump}")

    with open(args.dump, "r", encoding="utf-8") as fh:
        payload = json.load(fh)

    models_to_truncate = [
        Review,
        Tour,
        TourCategory,
        Service,
        ServiceCategory,
        NewsPost,
        BlogPost,
        PricePDF,
        Tag,
        Category,
    ]

    with transaction.atomic():
        truncate_models(models_to_truncate)
        restore_from_dump(payload)

    print("Restore completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
