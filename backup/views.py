# backup/views.py
import io
import os
import json
import zipfile
import tempfile
import shutil
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
from news.models import NewsPost
from blog.models import BlogPost
from core.models import Category, Tag, SiteSettings

MEDIA_ROOT = Path(settings.MEDIA_ROOT)


def _check_access(request):
    """Разрешаем суперпользователей, staff и пользователей в группах managers/Managers/менеджеры."""
    u = request.user
    if not getattr(u, "is_active", False):
        messages.error(request, "Доступ запрещён")
        return False
    in_managers = u.groups.filter(name__in=["managers", "Managers", "менеджеры"]).exists()
    if u.is_superuser or getattr(u, "is_staff", False) or in_managers:
        return True
    messages.error(request, "Доступ разрешён только администраторам и менеджерам")
    return False


# --- DOWNLOAD ---------------------------------------------------------------

@login_required
@require_http_methods(["GET"])
def backup_download(request):
    """Собирает ZIP: data/*.json + media/*."""
    if not _check_access(request):
        return redirect(reverse("admin:index"))

    now = datetime.utcnow().strftime("%Y%m%d")
    archive_name = f"TDP_{now}.zip"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # сериализация одной выборки в data/<name>.json
        def add_json(qs, name: str):
            data = []
            for obj in qs:
                row = {"pk": obj.pk}
                # простые поля + FK -> <field>_slug
                for field in obj._meta.fields:
                    if getattr(field, "many_to_many", False):
                        continue
                    fname = field.name
                    val = getattr(obj, fname)

                    # FK
                    if field.is_relation and val is not None:
                        row[f"{fname}_slug"] = getattr(val, "slug", None)
                        continue

                    # File/Image
                    if hasattr(val, "name"):
                        row[fname] = getattr(val, "name", None)
                        continue

                    # любые сериализуемые типы
                    try:
                        json.dumps(val)
                        row[fname] = val
                    except Exception:
                        row[fname] = str(val)

                # M2M: список slug
                m2m = {}
                for m in obj._meta.many_to_many:
                    m2m[m.name] = [
                        getattr(x, "slug", None) for x in getattr(obj, m.name).all()
                    ]
                if m2m:
                    row["_m2m"] = m2m

                data.append(row)

            z.writestr(f"data/{name}.json", json.dumps(data, ensure_ascii=False, indent=2))

        # порядок важен лишь для удобства
        add_json(Category.objects.all(), "categories")
        add_json(Tag.objects.all(), "tags")
        add_json(Tour.objects.all().select_related("category").prefetch_related("tags"), "tours")
        add_json(Service.objects.all().select_related("category").prefetch_related("tags"), "services")
        add_json(Review.objects.all(), "reviews")
        add_json(NewsPost.objects.all(), "news")
        add_json(BlogPost.objects.all(), "blog")

        # SiteSettings: без id
        ss = SiteSettings.objects.first()
        if ss:
            ss_data = {f.name: getattr(ss, f.name) for f in ss._meta.fields if f.name != "id"}
            z.writestr("data/site_settings.json", json.dumps(ss_data, ensure_ascii=False, indent=2))

        # media/*
        if MEDIA_ROOT.exists():
            for root, dirs, files in os.walk(MEDIA_ROOT):
                for f in files:
                    full = Path(root) / f
                    arc = str(full.relative_to(MEDIA_ROOT))
                    z.write(full, arcname=os.path.join("media", arc))

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=archive_name)


# --- RESTORE ----------------------------------------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def backup_restore(request):
    """
    Импортирует архив в рамках одной транзакции:
      - создает/обновляет Category/Tag
      - создает/обновляет Tour/Service с категорией
      - проставляет M2M-теги по slug
      - перезаписывает media/*
    На успех/ошибку показывает messages и возвращает на список.
    """
    if not _check_access(request):
        return redirect(reverse("admin:index"))

    # Если мы по ошибке пришли GET на /restore/, просто вернемся на список в админке
    if request.method == "GET":
        return redirect(reverse("admin:backup_backup_changelist"))

    # POST + файл
    archive = request.FILES.get("archive")
    if not archive:
        messages.error(request, "Не передан файл архива.")
        return redirect(reverse("admin:backup_backup_changelist"))

    if not archive.name.startswith("TDP_") or not archive.name.endswith(".zip"):
        messages.error(request, "Неверное имя архива. Ожидается TDP_YYYYMMDD.zip")
        return redirect(reverse("admin:backup_backup_changelist"))

    try:
        with transaction.atomic():
            tmpdir = tempfile.mkdtemp(prefix="tdp_restore_")
            tmp_p = Path(tmpdir)
            try:
                # распакуем
                with zipfile.ZipFile(archive, "r") as z:
                    z.extractall(tmpdir)

                data_dir = tmp_p / "data"

                def load_json(name: str):
                    p = data_dir / f"{name}.json"
                    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

                report = {"imported": {"categories": 0, "tags": 0, "tours": 0, "services": 0, "news": 0, "blog": 0}, "files": []}

                # 1) категории
                cat_map = {}
                for c in load_json("categories"):
                    slug = c.get("slug")
                    name = c.get("name") or slug
                    if not slug:
                        raise ValidationError("В categories найден объект без slug")
                    Category.objects.update_or_create(slug=slug, defaults={"name": name})
                    cat_map[c.get("pk")] = slug
                    report["imported"]["categories"] += 1

                # 2) теги
                tag_slugs = set()
                for t in load_json("tags"):
                    slug = t.get("slug")
                    name = t.get("name") or slug
                    if not slug:
                        raise ValidationError("В tags найден объект без slug")
                    Tag.objects.update_or_create(slug=slug, defaults={"name": name})
                    tag_slugs.add(slug)
                    report["imported"]["tags"] += 1

                # 3) туры
                for t in load_json("tours"):
                    tour_slug = t.get("slug") or f"restored-{t.get('pk')}"
                    # определяем категорию из category_slug или по старому pk
                    cat_slug = t.get("category_slug") or cat_map.get(t.get("category_id"))
                    if not cat_slug:
                        raise ValidationError(f"У тура '{tour_slug}' отсутствует категория")

                    try:
                        cat_obj = Category.objects.get(slug=cat_slug)
                    except Category.DoesNotExist:
                        raise ValidationError(f"Категория '{cat_slug}' не найдена при восстановлении тура '{tour_slug}'")

                    banned = {"pk", "_m2m", "created_at"}
                    defaults = {
                        k: v for k, v in t.items()
                        if k not in banned and not k.endswith("_id") and not k.endswith("_slug")
                    }
                    defaults["category"] = cat_obj
                    tour_obj, _ = Tour.objects.update_or_create(slug=tour_slug, defaults=defaults)
                    report["imported"]["tours"] += 1

                    # M2M теги
                    tag_list = [s for s in t.get("_m2m", {}).get("tags", []) if s]
                    if tag_list:
                        tour_obj.tags.set(Tag.objects.filter(slug__in=tag_list))

                # 4) сервисы
                for s in load_json("services"):
                    service_slug = s.get("slug") or f"restored-s-{s.get('pk')}"
                    cat_slug = s.get("category_slug") or cat_map.get(s.get("category_id"))
                    if not cat_slug:
                        raise ValidationError(f"У сервиса '{service_slug}' отсутствует категория")

                    try:
                        cat_obj = Category.objects.get(slug=cat_slug)
                    except Category.DoesNotExist:
                        raise ValidationError(f"Категория '{cat_slug}' не найдена при восстановлении сервиса '{service_slug}'")

                    banned = {"pk", "_m2m", "created_at"}
                    defaults = {
                        k: v for k, v in s.items()
                        if k not in banned and not k.endswith("_id") and not k.endswith("_slug")
                    }
                    defaults["category"] = cat_obj
                    svc_obj, _ = Service.objects.update_or_create(slug=service_slug, defaults=defaults)

                    report["imported"]["services"] += 1

                    tag_list = [ts for ts in s.get("_m2m", {}).get("tags", []) if ts]
                    if tag_list:
                        svc_obj.tags.set(Tag.objects.filter(slug__in=tag_list))

                # 5) новости
                for n in load_json("news"):
                    news_slug = n.get("slug") or f"restored-news-{n.get('pk')}"
                    banned = {"pk", "_m2m", "created_at", "pub_date"}
                    defaults = {k: v for k, v in n.items() if k not in banned and not k.endswith("_slug")}
                    NewsPost.objects.update_or_create(slug=news_slug, defaults=defaults)
                    report["imported"]["news"] += 1

                # 6) блог
                for b in load_json("blog"):
                    blog_slug = b.get("slug") or f"restored-blog-{b.get('pk')}"
                    banned = {"pk", "_m2m", "created_at", "pub_date"}
                    defaults = {k: v for k, v in b.items() if k not in banned and not k.endswith("_slug")}
                    BlogPost.objects.update_or_create(slug=blog_slug, defaults=defaults)
                    report["imported"]["blog"] += 1

                # 5) SiteSettings (опционально, один объект)
                ss = load_json("site_settings")
                if isinstance(ss, dict) and ss:
                    ss.pop("id", None)
                    SiteSettings.objects.all().delete()
                    SiteSettings.objects.create(**ss)

                # 6) media/*
                media_src = tmp_p / "media"
                if media_src.exists():
                    for root, dirs, files in os.walk(media_src):
                        for f in files:
                            src = Path(root) / f
                            rel = src.relative_to(media_src)
                            dst = MEDIA_ROOT / rel
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(src, dst)
                            report["files"].append(str(rel))

            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)

    except (IntegrityError, ValidationError, zipfile.BadZipFile, json.JSONDecodeError, FileNotFoundError) as e:
        messages.error(request, f"Ошибка восстановления: {e}")
        return redirect(reverse("admin:backup_backup_changelist"))
    except Exception as e:
        messages.error(request, f"Непредвиденная ошибка восстановления: {e}")
        return redirect(reverse("admin:backup_backup_changelist"))

    imp = report["imported"]
    messages.success(
        request,
        f"Импортировано: {imp.get('categories', 0)} категорий, "
        f"{imp.get('tags', 0)} тегов, {imp.get('tours', 0)} туров, "
        f"{imp.get('services', 0)} сервисов, {imp.get('news', 0)} новостей, {imp.get('blog', 0)} статей; "
        f"файлов медиа: {len(report['files'])}"
    )
    return redirect(reverse("admin:backup_backup_changelist"))


# --- НЕобязательные маршруты для вне-админки (если вдруг подключите) -------

@login_required
def backup_index(request):
    if not _check_access(request):
        return redirect(reverse("admin:index"))
    return render(request, "backup/index.html", {})
