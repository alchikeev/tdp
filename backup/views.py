import io
import os
import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from tours.models import Tour
from services.models import Service
from reviews.models import Review
from core.models import Category, Tag, SiteSettings


MEDIA_ROOT = Path(settings.MEDIA_ROOT)


def _check_access(request):
    """Разрешаем доступ суперпользователю, staff и пользователям из группы managers."""
    user = request.user
    if not getattr(user, "is_active", False):
        messages.error(request, "Доступ запрещён")
        return False

    in_managers = user.groups.filter(name__in=["managers", "Managers", "менеджеры"]).exists()
    if user.is_superuser or getattr(user, "is_staff", False) or in_managers:
        return True

    messages.error(request, "Доступ разрешён только администраторам и менеджерам")
    return False


@login_required
def backup_index(request):
    if not _check_access(request):
        return redirect(reverse("admin:index"))
    return render(request, "backup/index.html", {})


@login_required
@require_http_methods(["GET"])
def backup_download(request):
    """
    Экспортирует данные и медиа в ZIP:
      - data/categories.json
      - data/tags.json
      - data/tours.json
      - data/services.json
      - data/reviews.json
      - data/site_settings.json
      - media/***
    В JSON:
      * Простые поля как есть
      * FK -> <field>_slug
      * M2M -> _m2m: {field: [slug, ...]}
      * File/Image -> относительный путь (name)
    """
    if not _check_access(request):
        return redirect(reverse("admin:index"))

    now = datetime.utcnow().strftime("%Y%m%d")
    archive_name = f"TDP_{now}.zip"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:

        def add_json(qs, name: str):
            data = []
            for obj in qs:
                row = {"pk": obj.pk}
                # Обычные/FK поля
                for field in obj._meta.fields:
                    # (ManyToMany в _meta.fields нет, но оставим страховку)
                    if getattr(field, "many_to_many", False):
                        continue

                    fname = field.name
                    val = getattr(obj, fname)

                    # FK -> slug
                    if field.is_relation and val is not None:
                        row[f"{fname}_slug"] = getattr(val, "slug", None)
                        continue

                    # File/Image -> сохранить имя (относительный путь в MEDIA_ROOT)
                    if hasattr(val, "name"):
                        row[fname] = getattr(val, "name", None)
                        continue

                    # Простые типы
                    try:
                        json.dumps(val)
                        row[fname] = val
                    except Exception:
                        row[fname] = str(val)

                # M2M -> список slug
                m2m = {}
                for m in obj._meta.many_to_many:
                    m2m[m.name] = [
                        getattr(x, "slug", None)
                        for x in getattr(obj, m.name).all()
                        if getattr(x, "slug", None)
                    ]
                if m2m:
                    row["_m2m"] = m2m

                data.append(row)

            z.writestr(f"data/{name}.json", json.dumps(data, ensure_ascii=False, indent=2))

        # Экспорт данных
        add_json(Category.objects.all(), "categories")
        add_json(Tag.objects.all(), "tags")
        add_json(Tour.objects.select_related("category").prefetch_related("tags").all(), "tours")
        add_json(Service.objects.select_related("category").prefetch_related("tags").all(), "services")
        add_json(Review.objects.all(), "reviews")

        # SiteSettings (первый объект, без id)
        ss = SiteSettings.objects.first()
        if ss:
            ss_data = {f.name: getattr(ss, f.name) for f in ss._meta.fields if f.name != "id"}
            z.writestr("data/site_settings.json", json.dumps(ss_data, ensure_ascii=False, indent=2))

        # Медиа
        if MEDIA_ROOT.exists():
            for root, _, files in os.walk(MEDIA_ROOT):
                for f in files:
                    full = Path(root) / f
                    arc = str(full.relative_to(MEDIA_ROOT))
                    z.write(full, arcname=os.path.join("media", arc))

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=archive_name)


def _safe_extract_all(zf: zipfile.ZipFile, dest: Path):
    """Простая защита от Zip Slip."""
    dest = Path(dest).resolve()
    for member in zf.infolist():
        out_path = (dest / member.filename).resolve()
        if not str(out_path).startswith(str(dest)):
            raise ValidationError("Некорректный архив: обнаружен небезопасный путь")
        zf.extract(member, dest)


@login_required
@require_http_methods(["GET", "POST"])
def backup_restore(request):
    """
    Импортирует архив TDP_YYYYMMDD.zip:
      1) Распаковывает во временную папку
      2) Загружает data/*.json в порядке: categories -> tags -> tours -> services -> reviews -> site_settings
         - FK восстанавливаются по *_slug (категории/теги должны существовать к моменту загрузки)
         - M2M (tags) ставятся по slug
      3) Копирует media/ в MEDIA_ROOT с перезаписью
      4) Всё в transaction.atomic(); при ошибке делаем rollback и показываем messages.error
    """
    if not _check_access(request):
        return redirect(reverse("admin:index"))

    report = {"imported": {}, "files": []}

    if request.method == "POST" and request.FILES.get("archive"):
        archive = request.FILES["archive"]

        # Простая валидация имени
        if not archive.name.startswith("TDP_") or not archive.name.endswith(".zip"):
            messages.error(request, "Неправильный формат архива. Ожидается TDP_YYYYMMDD.zip")
            return redirect(reverse("admin:backup_backup_changelist"))

        try:
            with transaction.atomic():
                tmp_dir = tempfile.mkdtemp(prefix="tdp_restore_")
                tmp_p = Path(tmp_dir)
                try:
                    with zipfile.ZipFile(archive, "r") as z:
                        _safe_extract_all(z, tmp_p)

                    data_dir = tmp_p / "data"

                    def load_json(name: str):
                        p = data_dir / f"{name}.json"
                        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

                    # --- Categories ---
                    cats = load_json("categories")
                    cat_map = {}
                    report["imported"]["categories"] = 0
                    for c in cats:
                        slug = c.get("slug")
                        if not slug:
                            # пропускаем "битую" запись
                            continue
                        name = c.get("name") or slug
                        Category.objects.update_or_create(slug=slug, defaults={"name": name})
                        cat_map[c.get("pk")] = slug
                        report["imported"]["categories"] += 1

                    # --- Tags ---
                    tags = load_json("tags")
                    tag_map = {}
                    report["imported"]["tags"] = 0
                    for t in tags:
                        slug = t.get("slug")
                        if not slug:
                            continue
                        name = t.get("name") or slug
                        Tag.objects.update_or_create(slug=slug, defaults={"name": name})
                        tag_map[t.get("pk")] = slug
                        report["imported"]["tags"] += 1

                    # --- Tours ---
                    report["imported"]["tours"] = 0
                    for t in load_json("tours"):
                        tour_slug = t.get("slug") or f"restored-{t.get('pk')}"
                        # FK категория (по *_slug или по старому pk через карту)
                        cat_slug = t.get("category_slug") or cat_map.get(t.get("category_id"))
                        if not cat_slug:
                            raise ValidationError(f"У тура '{tour_slug}' нет категории")
                        try:
                            cat_obj = Category.objects.get(slug=cat_slug)
                        except Category.DoesNotExist:
                            raise ValidationError(f"Категория '{cat_slug}' не найдена для тура '{tour_slug}'")

                        # Готовим defaults: удаляем id/pk, *_id, *_slug (кроме собственного slug), служебные поля
                        banned = {"pk", "id", "_m2m", "created_at", "category_id", "category_slug"}
                        defaults = {
                            k: v
                            for k, v in t.items()
                            if k not in banned
                            and not k.endswith("_id")
                            and not (k.endswith("_slug") and k != "slug")
                        }
                        defaults["category"] = cat_obj

                        tour_obj, _ = Tour.objects.update_or_create(slug=tour_slug, defaults=defaults)
                        report["imported"]["tours"] += 1

                        # M2M tags
                        tag_slugs = [s for s in t.get("_m2m", {}).get("tags", []) if s]
                        if tag_slugs:
                            tour_obj.tags.set(Tag.objects.filter(slug__in=tag_slugs))
                        else:
                            tour_obj.tags.clear()

                    # --- Services ---
                    report["imported"]["services"] = 0
                    for s in load_json("services"):
                        service_slug = s.get("slug") or f"restored-s-{s.get('pk')}"
                        cat_slug = s.get("category_slug") or cat_map.get(s.get("category_id"))
                        if not cat_slug:
                            raise ValidationError(f"У сервиса '{service_slug}' нет категории")
                        try:
                            cat_obj = Category.objects.get(slug=cat_slug)
                        except Category.DoesNotExist:
                            raise ValidationError(f"Категория '{cat_slug}' не найдена для сервиса '{service_slug}'")

                        banned = {"pk", "id", "_m2m", "created_at", "category_id", "category_slug"}
                        defaults = {
                            k: v
                            for k, v in s.items()
                            if k not in banned
                            and not k.endswith("_id")
                            and not (k.endswith("_slug") and k != "slug")
                        }
                        defaults["category"] = cat_obj

                        svc_obj, _ = Service.objects.update_or_create(slug=service_slug, defaults=defaults)
                        report["imported"]["services"] += 1

                        tag_slugs = [ts for ts in s.get("_m2m", {}).get("tags", []) if ts]
                        if tag_slugs:
                            svc_obj.tags.set(Tag.objects.filter(slug__in=tag_slugs))
                        else:
                            svc_obj.tags.clear()

                    # --- Reviews (простая загрузка; без связей на пользователей) ---
                    # Если структура модели расширится, можно добавить поля в список ниже.
                    report["imported"]["reviews"] = 0
                    for r in load_json("reviews"):
                        defaults = {
                            k: r[k]
                            for k in ["name", "email", "message", "is_approved", "created_at"]
                            if k in r
                        }
                        # Совпадение по pk (если занят — будет обновление)
                        Review.objects.update_or_create(pk=r.get("pk"), defaults=defaults)
                        report["imported"]["reviews"] += 1

                    # --- SiteSettings ---
                    ss_data = load_json("site_settings")
                    if ss_data:
                        if isinstance(ss_data, list):
                            ss_data = (ss_data or [{}])[0]
                        ss_data.pop("id", None)
                        SiteSettings.objects.all().delete()
                        SiteSettings.objects.create(**ss_data)
                        report["imported"]["site_settings"] = 1

                    # --- Media ---
                    media_src = tmp_p / "media"
                    if media_src.exists():
                        for root, _, files in os.walk(media_src):
                            for f in files:
                                src = Path(root) / f
                                rel = src.relative_to(media_src)
                                dst = MEDIA_ROOT / rel
                                dst.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(src, dst)
                                report["files"].append(str(rel))

                finally:
                    shutil.rmtree(tmp_p, ignore_errors=True)

        except (IntegrityError, ValidationError, zipfile.BadZipFile, json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            messages.error(request, f"Ошибка восстановления: {e}")
            return redirect(reverse("admin:backup_backup_changelist"))

        imp = report.get("imported", {})
        messages.success(
            request,
            (
                "Восстановление завершено. "
                f"Категорий: {imp.get('categories', 0)}, "
                f"тегов: {imp.get('tags', 0)}, "
                f"туров: {imp.get('tours', 0)}, "
                f"сервисов: {imp.get('services', 0)}, "
                f"отзывов: {imp.get('reviews', 0)}, "
                f"файлов медиа: {len(report.get('files', []))}."
            ),
        )
        return redirect(reverse("admin:backup_backup_changelist"))

    return render(request, "backup/restore.html", {"report": report})
