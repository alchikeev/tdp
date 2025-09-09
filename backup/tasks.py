import io
import os
import json
import zipfile
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.utils import timezone

from .models import RestoreTask
from tours.models import Tour, TourCategory
from services.models import Service, ServiceCategory
from reviews.models import Review
from news.models import NewsPost
from blog.models import BlogPost
from prices.models import PricePDF
from core.models import Category, Tag, SiteSettings


@shared_task(bind=True)
def restore_backup_task(self, task_id, file_path):
    """
    Фоновая задача для восстановления архива
    """
    task = RestoreTask.objects.get(id=task_id)
    
    try:
        # Обновляем статус на "обрабатывается"
        task.status = 'processing'
        task.started_at = timezone.now()
        task.progress = 0
        task.message = 'Начинаем восстановление...'
        task.save()
        
        # Обновляем прогресс через Celery
        self.update_state(
            state='PROGRESS',
            meta={'progress': 0, 'message': 'Начинаем восстановление...'}
        )
        
        with transaction.atomic():
            tmpdir = tempfile.mkdtemp(prefix="tdp_restore_")
            tmp_p = Path(tmpdir)
            
            try:
                # Распаковываем архив (5%)
                task.message = 'Распаковка архива...'
                task.progress = 5
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 5, 'message': 'Распаковка архива...'}
                )
                
                with zipfile.ZipFile(file_path, "r") as z:
                    z.extractall(tmpdir)
                
                data_dir = tmp_p / "data"
                
                # Очищаем старые данные (10%)
                task.message = 'Очистка старых данных...'
                task.progress = 10
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 10, 'message': 'Очистка старых данных...'}
                )
                
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
                
                # Импорт категорий (20%)
                task.message = 'Импорт категорий...'
                task.progress = 20
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 20, 'message': 'Импорт категорий...'}
                )
                
                cat_map = {}
                for c in load_json("categories"):
                    slug = c.get("slug")
                    name = c.get("name") or slug
                    if not slug:
                        raise ValidationError("В categories найден объект без slug")
                    Category.objects.update_or_create(slug=slug, defaults={"name": name})
                    cat_map[c.get("pk")] = slug
                    task.imported_categories += 1
                
                # Импорт категорий туров (30%)
                task.message = 'Импорт категорий туров...'
                task.progress = 30
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 30, 'message': 'Импорт категорий туров...'}
                )
                
                for tc in load_json("tour_categories"):
                    slug = tc.get("slug")
                    name = tc.get("name") or slug
                    parent_slug = tc.get("parent_slug")
                    parent = TourCategory.objects.filter(slug=parent_slug).first() if parent_slug else None
                    TourCategory.objects.update_or_create(slug=slug, defaults={"name": name, "parent": parent})
                
                # Импорт категорий услуг (35%)
                task.message = 'Импорт категорий услуг...'
                task.progress = 35
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 35, 'message': 'Импорт категорий услуг...'}
                )
                
                for sc in load_json("service_categories"):
                    slug = sc.get("slug")
                    name = sc.get("name") or slug
                    parent_slug = sc.get("parent_slug")
                    parent = ServiceCategory.objects.filter(slug=parent_slug).first() if parent_slug else None
                    ServiceCategory.objects.update_or_create(slug=slug, defaults={"name": name, "parent": parent})
                
                # Импорт тегов (40%)
                task.message = 'Импорт тегов...'
                task.progress = 40
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 40, 'message': 'Импорт тегов...'}
                )
                
                tag_slugs = set()
                for t in load_json("tags"):
                    slug = t.get("slug")
                    name = t.get("name") or slug
                    if not slug:
                        raise ValidationError("В tags найден объект без slug")
                    Tag.objects.update_or_create(slug=slug, defaults={"name": name})
                    tag_slugs.add(slug)
                    task.imported_tags += 1
                
                # Импорт туров (50%)
                task.message = 'Импорт туров...'
                task.progress = 50
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 50, 'message': 'Импорт туров...'}
                )
                
                for t in load_json("tours"):
                    tour_slug = t.get("slug") or f"restored-{t.get('pk')}"
                    banned = {"pk", "_m2m", "created_at"}
                    defaults = {
                        k: v for k, v in t.items()
                        if k not in banned and not k.endswith("_id") and not k.endswith("_slug")
                    }
                    tour_obj, _ = Tour.objects.update_or_create(slug=tour_slug, defaults=defaults)
                    task.imported_tours += 1
                    
                    # M2M категории
                    cat_list = [s for s in t.get("_m2m", {}).get("categories", []) if s]
                    if cat_list:
                        tour_obj.categories.set(TourCategory.objects.filter(slug__in=cat_list))
                    
                    # M2M теги
                    tag_list = [s for s in t.get("_m2m", {}).get("tags", []) if s]
                    if tag_list:
                        tour_obj.tags.set(Tag.objects.filter(slug__in=tag_list))
                
                # Импорт услуг (60%)
                task.message = 'Импорт услуг...'
                task.progress = 60
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 60, 'message': 'Импорт услуг...'}
                )
                
                for s in load_json("services"):
                    service_slug = s.get("slug") or f"restored-s-{s.get('pk')}"
                    banned = {"pk", "_m2m", "created_at"}
                    defaults = {
                        k: v for k, v in s.items()
                        if k not in banned and not k.endswith("_id") and not k.endswith("_slug")
                    }
                    svc_obj, _ = Service.objects.update_or_create(slug=service_slug, defaults=defaults)
                    task.imported_services += 1
                    
                    # M2M категории
                    cat_list = [slug for slug in s.get("_m2m", {}).get("categories", []) if slug]
                    if cat_list:
                        svc_obj.categories.set(ServiceCategory.objects.filter(slug__in=cat_list))
                    
                    # M2M теги
                    tag_list = [ts for ts in s.get("_m2m", {}).get("tags", []) if ts]
                    if tag_list:
                        svc_obj.tags.set(Tag.objects.filter(slug__in=tag_list))
                
                # Импорт отзывов (65%)
                task.message = 'Импорт отзывов...'
                task.progress = 65
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 65, 'message': 'Импорт отзывов...'}
                )
                
                for r in load_json("reviews"):
                    banned = {"pk"}
                    defaults = {k: v for k, v in r.items() if k not in banned}
                    Review.objects.create(**defaults)
                    task.imported_reviews += 1
                
                # Импорт новостей (70%)
                task.message = 'Импорт новостей...'
                task.progress = 70
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 70, 'message': 'Импорт новостей...'}
                )
                
                for n in load_json("news"):
                    news_slug = n.get("slug") or f"restored-news-{n.get('pk')}"
                    banned = {"pk", "_m2m", "created_at", "pub_date"}
                    defaults = {k: v for k, v in n.items() if k not in banned and not k.endswith("_slug")}
                    NewsPost.objects.update_or_create(slug=news_slug, defaults=defaults)
                    task.imported_news += 1
                
                # Импорт блога (75%)
                task.message = 'Импорт статей блога...'
                task.progress = 75
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 75, 'message': 'Импорт статей блога...'}
                )
                
                for b in load_json("blog"):
                    blog_slug = b.get("slug") or f"restored-blog-{b.get('pk')}"
                    banned = {"pk", "_m2m", "created_at", "pub_date"}
                    defaults = {k: v for k, v in b.items() if k not in banned and not k.endswith("_slug")}
                    BlogPost.objects.update_or_create(slug=blog_slug, defaults=defaults)
                    task.imported_blog += 1
                
                # Импорт прайсов (80%)
                task.message = 'Импорт прайсов...'
                task.progress = 80
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 80, 'message': 'Импорт прайсов...'}
                )
                
                PricePDF.objects.all().delete()
                for p in load_json("prices"):
                    data = {k: v for k, v in p.items() if k not in {"pk", "uploaded_at"}}
                    PricePDF.objects.create(**data)
                    task.imported_prices += 1
                
                # Импорт настроек сайта (85%)
                task.message = 'Импорт настроек сайта...'
                task.progress = 85
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 85, 'message': 'Импорт настроек сайта...'}
                )
                
                ss = load_json("site_settings")
                if isinstance(ss, dict) and ss:
                    ss.pop("id", None)
                    SiteSettings.objects.all().delete()
                    SiteSettings.objects.create(**ss)
                
                # Импорт медиа файлов (90%)
                task.message = 'Импорт медиа файлов...'
                task.progress = 90
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 90, 'message': 'Импорт медиа файлов...'}
                )
                
                media_src = tmp_p / "media"
                if media_src.exists():
                    media_root = Path(settings.MEDIA_ROOT)
                    media_root.mkdir(parents=True, exist_ok=True)
                    
                    for root, dirs, files in os.walk(media_src):
                        for f in files:
                            src = Path(root) / f
                            rel = src.relative_to(media_src)
                            dst = media_root / rel
                            
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(src, dst)
                            task.imported_files += 1
                
                # Импорт базы данных (95%)
                task.message = 'Импорт базы данных...'
                task.progress = 95
                task.save()
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': 95, 'message': 'Импорт базы данных...'}
                )
                
                db_src = tmp_p / "data" / "db.sqlite3"
                if db_src.exists():
                    data_root = Path(settings.DATABASES['default']['NAME'])
                    data_root.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(db_src, data_root)
                
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)
        
        # Завершение (100%)
        task.status = 'completed'
        task.progress = 100
        task.completed_at = timezone.now()
        task.message = f'Восстановление завершено успешно! Импортировано: {task.imported_categories} категорий, {task.imported_tags} тегов, {task.imported_tours} туров, {task.imported_services} услуг, {task.imported_reviews} отзывов, {task.imported_news} новостей, {task.imported_blog} статей, {task.imported_prices} прайсов, {task.imported_files} файлов.'
        task.save()
        
        self.update_state(
            state='SUCCESS',
            meta={'progress': 100, 'message': 'Восстановление завершено успешно!'}
        )
        
        return {
            'status': 'completed',
            'message': 'Восстановление завершено успешно!',
            'imported': {
                'categories': task.imported_categories,
                'tags': task.imported_tags,
                'tours': task.imported_tours,
                'services': task.imported_services,
                'reviews': task.imported_reviews,
                'news': task.imported_news,
                'blog': task.imported_blog,
                'prices': task.imported_prices,
                'files': task.imported_files,
            }
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        task.status = 'failed'
        task.error_details = error_details
        task.message = f'Ошибка восстановления: {str(e)}'
        task.completed_at = timezone.now()
        task.save()
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'details': error_details}
        )
        
        raise e
