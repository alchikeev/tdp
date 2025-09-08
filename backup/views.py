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

from tours.models import Tour, TourCategory
from services.models import Service, ServiceCategory
from reviews.models import Review
from news.models import NewsPost
from blog.models import BlogPost
from prices.models import PricePDF
from core.models import Category, Tag, SiteSettings


def get_media_root():
    """Получает правильный путь к медиа файлам в зависимости от окружения"""
    if settings.DEBUG:
        # В dev режиме используем локальную папку
        path = Path(settings.MEDIA_ROOT)
    else:
        # В prod режиме используем путь в контейнере
        path = Path(settings.MEDIA_ROOT)
    
    print(f"DEBUG: MEDIA_ROOT = {path} (DEBUG={settings.DEBUG})")
    return path


def get_data_root():
    """Получает правильный путь к базе данных в зависимости от окружения"""
    if settings.DEBUG:
        # В dev режиме используем локальную папку
        path = Path(settings.BASE_DIR) / "db.sqlite3"
    else:
        # В prod режиме используем путь в контейнере
        path = Path("/app/data/db.sqlite3")
    
    print(f"DEBUG: DATA_ROOT = {path} (DEBUG={settings.DEBUG})")
    return path


def get_static_root():
    """Получает правильный путь к статическим файлам в зависимости от окружения"""
    if settings.DEBUG:
        # В dev режиме используем локальную папку
        path = Path(settings.STATIC_ROOT)
    else:
        # В prod режиме используем путь в контейнере
        path = Path(settings.STATIC_ROOT)
    
    print(f"DEBUG: STATIC_ROOT = {path} (DEBUG={settings.DEBUG})")
    return path


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
        # порядок важен лишь для удобства
        add_json(Category.objects.all(), "categories")
        add_json(Tag.objects.all(), "tags")
        # таксономии для туров и услуг
        add_json(TourCategory.objects.all(), "tour_categories")
        add_json(ServiceCategory.objects.all(), "service_categories")
        add_json(Tour.objects.all().prefetch_related("categories", "tags"), "tours")
        add_json(Service.objects.all().prefetch_related("categories", "tags"), "services")
        add_json(Review.objects.all(), "reviews")
        add_json(NewsPost.objects.all(), "news")
        add_json(BlogPost.objects.all(), "blog")
        add_json(PricePDF.objects.all(), "prices")

        # SiteSettings: без id
        ss = SiteSettings.objects.first()
        if ss:
            ss_data = {f.name: getattr(ss, f.name) for f in ss._meta.fields if f.name != "id"}
            z.writestr("data/site_settings.json", json.dumps(ss_data, ensure_ascii=False, indent=2))

        # media/*
        media_root = get_media_root()
        if media_root.exists():
            for root, dirs, files in os.walk(media_root):
                for f in files:
                    full = Path(root) / f
                    arc = str(full.relative_to(media_root))
                    z.write(full, arcname=os.path.join("media", arc))

        # database/*
        data_root = get_data_root()
        if data_root.exists():
            # Копируем базу данных
            z.write(data_root, arcname="data/db.sqlite3")

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
                # --- Очищаем старые данные перед восстановлением ---
                SiteSettings.objects.all().delete()
                BlogPost.objects.all().delete()
                NewsPost.objects.all().delete()
                Review.objects.all().delete()
                Service.objects.all().delete()
                ServiceCategory.objects.all().delete()
                Tour.objects.all().delete()
                TourCategory.objects.all().delete()
                Tag.objects.all().delete()
                Category.objects.all().delete()

                def load_json(name: str):
                    p = data_dir / f"{name}.json"
                    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

                report = {"imported": {"categories": 0, "tags": 0, "tours": 0, "services": 0, "reviews": 0, "news": 0, "blog": 0, "prices": 0}, "files": []}

                # 1) категории (core)
                cat_map = {}
                for c in load_json("categories"):
                    slug = c.get("slug")
                    name = c.get("name") or slug
                    if not slug:
                        raise ValidationError("В categories найден объект без slug")
                    # core Category
                    Category.objects.update_or_create(slug=slug, defaults={"name": name})
                    cat_map[c.get("pk")] = slug
                    report["imported"]["categories"] += 1

                # 2) категории туров из JSON
                for tc in load_json("tour_categories"):
                    slug = tc.get("slug")
                    name = tc.get("name") or slug
                    parent_slug = tc.get("parent_slug")
                    parent = TourCategory.objects.filter(slug=parent_slug).first() if parent_slug else None
                    TourCategory.objects.update_or_create(slug=slug, defaults={"name": name, "parent": parent})

                # 3) категории услуг из JSON
                for sc in load_json("service_categories"):
                    slug = sc.get("slug")
                    name = sc.get("name") or slug
                    parent_slug = sc.get("parent_slug")
                    parent = ServiceCategory.objects.filter(slug=parent_slug).first() if parent_slug else None
                    ServiceCategory.objects.update_or_create(slug=slug, defaults={"name": name, "parent": parent})

                # 4) теги
                tag_slugs = set()
                for t in load_json("tags"):
                    slug = t.get("slug")
                    name = t.get("name") or slug
                    if not slug:
                        raise ValidationError("В tags найден объект без slug")
                    Tag.objects.update_or_create(slug=slug, defaults={"name": name})
                    tag_slugs.add(slug)
                    report["imported"]["tags"] += 1

                # 5) туры (TourCategory -> categories)
                for t in load_json("tours"):
                    tour_slug = t.get("slug") or f"restored-{t.get('pk')}"
                    # Основные поля, без M2M
                    banned = {"pk", "_m2m", "created_at"}
                    defaults = {
                        k: v for k, v in t.items()
                        if k not in banned and not k.endswith("_id") and not k.endswith("_slug")
                    }
                    tour_obj, _ = Tour.objects.update_or_create(slug=tour_slug, defaults=defaults)
                    report["imported"]["tours"] += 1

                    # M2M категории
                    cat_list = [s for s in t.get("_m2m", {}).get("categories", []) if s]
                    if cat_list:
                        tour_obj.categories.set(TourCategory.objects.filter(slug__in=cat_list))

                    # M2M теги
                    tag_list = [s for s in t.get("_m2m", {}).get("tags", []) if s]
                    if tag_list:
                        tour_obj.tags.set(Tag.objects.filter(slug__in=tag_list))

                # 6) сервисы (ServiceCategory -> categories)
                for s in load_json("services"):
                    service_slug = s.get("slug") or f"restored-s-{s.get('pk')}"
                    # Основные поля, без M2M
                    banned = {"pk", "_m2m", "created_at"}
                    defaults = {
                        k: v for k, v in s.items()
                        if k not in banned and not k.endswith("_id") and not k.endswith("_slug")
                    }
                    svc_obj, _ = Service.objects.update_or_create(slug=service_slug, defaults=defaults)
                    report["imported"]["services"] += 1

                    # M2M категории
                    cat_list = [slug for slug in s.get("_m2m", {}).get("categories", []) if slug]
                    if cat_list:
                        svc_obj.categories.set(ServiceCategory.objects.filter(slug__in=cat_list))

                    # M2M теги
                    tag_list = [ts for ts in s.get("_m2m", {}).get("tags", []) if ts]
                    if tag_list:
                        svc_obj.tags.set(Tag.objects.filter(slug__in=tag_list))
                # 7) отзывы
                for r in load_json("reviews"):
                    banned = {"pk"}
                    defaults = {k: v for k, v in r.items() if k not in banned}
                    Review.objects.create(**defaults)
                    report["imported"]["reviews"] += 1

                # 8) новости
                for n in load_json("news"):
                    news_slug = n.get("slug") or f"restored-news-{n.get('pk')}"
                    banned = {"pk", "_m2m", "created_at", "pub_date"}
                    defaults = {k: v for k, v in n.items() if k not in banned and not k.endswith("_slug")}
                    NewsPost.objects.update_or_create(slug=news_slug, defaults=defaults)
                    report["imported"]["news"] += 1

                # 9) блог
                for b in load_json("blog"):
                    blog_slug = b.get("slug") or f"restored-blog-{b.get('pk')}"
                    banned = {"pk", "_m2m", "created_at", "pub_date"}
                    defaults = {k: v for k, v in b.items() if k not in banned and not k.endswith("_slug")}
                    BlogPost.objects.update_or_create(slug=blog_slug, defaults=defaults)
                    report["imported"]["blog"] += 1

                # 10) прайсы (PricePDF)
                PricePDF.objects.all().delete()
                for p in load_json("prices"):
                    data = {k: v for k, v in p.items() if k not in {"pk", "uploaded_at"}}
                    PricePDF.objects.create(**data)
                    report["imported"]["prices"] += 1

                # 11) SiteSettings (опционально, один объект)
                ss = load_json("site_settings")
                if isinstance(ss, dict) and ss:
                    ss.pop("id", None)
                    SiteSettings.objects.all().delete()
                    SiteSettings.objects.create(**ss)

                # 6) media/*
                media_src = tmp_p / "media"
                if media_src.exists():
                    # Убеждаемся, что MEDIA_ROOT существует и доступен для записи
                    media_root = get_media_root()
                    media_root.mkdir(parents=True, exist_ok=True)
                    
                    for root, dirs, files in os.walk(media_src):
                        for f in files:
                            src = Path(root) / f
                            rel = src.relative_to(media_src)
                            dst = media_root / rel
                            
                            # Создаем директорию с правами на запись
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Копируем файл
                            shutil.copy2(src, dst)
                            report["files"].append(str(rel))

                # 7) database/*
                db_src = tmp_p / "data" / "db.sqlite3"
                if db_src.exists():
                    # Убеждаемся, что директория для базы данных существует
                    data_root = get_data_root()
                    data_root.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Копируем базу данных
                    shutil.copy2(db_src, data_root)
                    report["files"].append("db.sqlite3")

            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)

    except (IntegrityError, ValidationError, zipfile.BadZipFile, json.JSONDecodeError, FileNotFoundError) as e:
        messages.error(request, f"Ошибка восстановления: {e}")
        return redirect(reverse("admin:backup_backup_changelist"))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        messages.error(request, f"Непредвиденная ошибка восстановления: {e}")
        print(f"Ошибка восстановления: {error_details}")  # Для отладки
        return redirect(reverse("admin:backup_backup_changelist"))

    imp = report["imported"]
    messages.success(
        request,
        f"Импортировано: {imp.get('categories', 0)} категорий, "
        f"{imp.get('tags', 0)} тегов, {imp.get('tours', 0)} туров, "
        f"{imp.get('services', 0)} сервисов, {imp.get('reviews', 0)} отзывов, "
        f"{imp.get('news', 0)} новостей, {imp.get('blog', 0)} статей, {imp.get('prices', 0)} прайсов; "
        f"файлов медиа: {len(report['files'])}"
    )
    return redirect(reverse("admin:backup_backup_changelist"))


# --- НЕобязательные маршруты для вне-админки (если вдруг подключите) -------

@login_required
def backup_index(request):
    if not _check_access(request):
        return redirect(reverse("admin:index"))
    return render(request, "backup/index.html", {})
