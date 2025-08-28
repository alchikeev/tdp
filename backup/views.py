import io
import os
import zipfile
import json
import tempfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

# Поддерживаемые модели для сериализации
from tours.models import Tour, TourImage
from services.models import Service, ServiceImage
from reviews.models import Review
from core.models import Category, Tag, SiteSettings

MEDIA_ROOT = Path(settings.MEDIA_ROOT)


def _check_access(request):
    """Allow access to superusers, staff admins and users in group 'managers'."""
    user = request.user
    if not getattr(user, 'is_active', False):
        messages.error(request, 'Доступ запрещён')
        return False

    # Разрешаем: суперпользователь, staff, либо пользователь в группе managers
    in_managers = user.groups.filter(name__in=['managers', 'Managers', 'менеджеры']).exists()
    if user.is_superuser or getattr(user, 'is_staff', False) or in_managers:
        return True

    messages.error(request, 'Доступ разрешён только администраторам и менеджерам')
    return False


@login_required
def backup_index(request):
    if not _check_access(request):
        return redirect(reverse('admin:index'))
    return render(request, 'backup/index.html', {})


@login_required
@require_http_methods(['GET'])
def backup_download(request):
    """Собирает ZIP архив с данными и медиа и отдает его как скачиваемый файл"""
    if not _check_access(request):
        return redirect(reverse('admin:index'))

    now = datetime.utcnow().strftime('%Y%m%d')
    archive_name = f"TDP_{now}.zip"

    # Создаем ZIP в памяти
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        # 1) сериализуем данные моделей в JSON-файлы
        def add_json(qs, name):
            data = []
            for obj in qs:
                # простая сериализация: поля и связанные slugs
                row = { 'pk': obj.pk }
                for field in obj._meta.fields:
                    if field.many_to_many or field.one_to_many:
                        continue
                    fname = field.name
                    val = getattr(obj, fname)
                    # для ImageField — сохраняем путь
                    if hasattr(val, 'url') or hasattr(val, 'name'):
                        row[fname] = getattr(val, 'name', None)
                    else:
                        # простые типы
                        try:
                            json.dumps(val)
                            row[fname] = val
                        except Exception:
                            row[fname] = str(val)
                # м2м поля (tags)
                m2m = {}
                for m in obj._meta.many_to_many:
                    m2m[m.name] = [getattr(x, 'slug', getattr(x, 'pk', None)) for x in getattr(obj, m.name).all()]
                if m2m:
                    row['_m2m'] = m2m
                data.append(row)
            z.writestr(f'data/{name}.json', json.dumps(data, ensure_ascii=False, indent=2))

        add_json(Tour.objects.all().select_related('category').prefetch_related('tags'), 'tours')
        add_json(Service.objects.all().select_related('category').prefetch_related('tags'), 'services')
        add_json(Review.objects.all(), 'reviews')

        # SiteSettings — сериализуем первый объект
        try:
            ss = SiteSettings.objects.first()
            if ss:
                ss_data = { f.name: getattr(ss, f.name) for f in ss._meta.fields }
                z.writestr('data/site_settings.json', json.dumps(ss_data, ensure_ascii=False, indent=2))
        except Exception:
            pass

        # 2) добавляем все файлы из MEDIA_ROOT
        if MEDIA_ROOT.exists():
            for root, dirs, files in os.walk(MEDIA_ROOT):
                for f in files:
                    full = Path(root) / f
                    arcname = str(full.relative_to(MEDIA_ROOT))
                    z.write(full, arcname=os.path.join('media', arcname))

    buf.seek(0)
    response = FileResponse(buf, as_attachment=True, filename=archive_name)
    return response


@login_required
@require_http_methods(['GET', 'POST'])
def backup_restore(request):
    """Загружает ZIP и подменяет данные/медиа из архива. Очень простая логика:
    - распаковать архив в tempdir
    - прочитать data/*.json и выполнить UPSERT по slug/pk
    - скопировать файлы в MEDIA_ROOT, перезаписав существующие
    - показать отчет о восстановлении
    """
    if not _check_access(request):
        return redirect(reverse('admin:index'))

    report = { 'imported': {}, 'files': [] }

    if request.method == 'POST' and request.FILES.get('archive'):
        archive = request.FILES['archive']
        # базовая валидация имени
        if not archive.name.startswith('TDP_') or not archive.name.endswith('.zip'):
            messages.error(request, 'Неправильный формат архива. Ожидается TDP_YYYYMMDD.zip')
            return redirect(reverse('backup:index'))

        tmpdir = tempfile.mkdtemp(prefix='tdp_restore_')
        tmpdir_p = Path(tmpdir)
        try:
            with zipfile.ZipFile(archive, 'r') as z:
                z.extractall(tmpdir)

            data_dir = tmpdir_p / 'data'
            if data_dir.exists():
                # вспомогательная загрузка JSON
                def load_json(name):
                    p = data_dir / f"{name}.json"
                    if not p.exists():
                        return []
                    return json.loads(p.read_text(encoding='utf-8'))

                # Восстановление категорий/тегов по имени/slug — аккуратно
                # Категории
                cats = load_json('categories') if (data_dir / 'categories.json').exists() else []
                for c in cats:
                    obj, created = Category.objects.update_or_create(slug=c.get('slug'), defaults={'name': c.get('name')})
                    report['imported'].setdefault('categories', 0)
                    report['imported']['categories'] = report['imported']['categories'] + (1 if created else 0)

                # Теги
                tgs = load_json('tags') if (data_dir / 'tags.json').exists() else []
                for t in tgs:
                    obj, created = Tag.objects.update_or_create(slug=t.get('slug'), defaults={'name': t.get('name')})
                    report['imported'].setdefault('tags', 0)
                    report['imported']['tags'] = report['imported']['tags'] + (1 if created else 0)

                # Tours
                tours = load_json('tours')
                for t in tours:
                    defaults = {}
                    for k, v in t.items():
                        if k in ('pk', '_m2m'):
                            continue
                        defaults[k] = v
                    # связанная категория — попытаемся найти
                    cat_slug = defaults.pop('category_id', None) or defaults.pop('category', None)
                    if cat_slug:
                        try:
                            cat = Category.objects.filter(pk=cat_slug).first() or Category.objects.filter(slug=cat_slug).first()
                            if cat:
                                defaults['category'] = cat
                        except Exception:
                            pass
                    obj, created = Tour.objects.update_or_create(slug=defaults.get('slug') or f"restored-{t.get('pk')}", defaults=defaults)
                    report['imported'].setdefault('tours', 0)
                    report['imported']['tours'] += 1
                    # м2м теги
                    if t.get('_m2m') and t['_m2m'].get('tags'):
                        slugs = t['_m2m']['tags']
                        tag_objs = []
                        for s in slugs:
                            tg = Tag.objects.filter(slug=s).first() or Tag.objects.filter(pk=s).first()
                            if tg:
                                tag_objs.append(tg)
                        if tag_objs:
                            obj.tags.set(tag_objs)

                # Services
                services = load_json('services')
                for s in services:
                    defaults = {}
                    for k, v in s.items():
                        if k in ('pk', '_m2m'):
                            continue
                        defaults[k] = v
                    cat_slug = defaults.pop('category_id', None) or defaults.pop('category', None)
                    if cat_slug:
                        try:
                            cat = Category.objects.filter(pk=cat_slug).first() or Category.objects.filter(slug=cat_slug).first()
                            if cat:
                                defaults['category'] = cat
                        except Exception:
                            pass
                    obj, created = Service.objects.update_or_create(slug=defaults.get('slug') or f"restored-s-{s.get('pk')}", defaults=defaults)
                    report['imported'].setdefault('services', 0)
                    report['imported']['services'] += 1
                    if s.get('_m2m') and s['_m2m'].get('tags'):
                        slugs = s['_m2m']['tags']
                        tag_objs = []
                        for sl in slugs:
                            tg = Tag.objects.filter(slug=sl).first() or Tag.objects.filter(pk=sl).first()
                            if tg:
                                tag_objs.append(tg)
                        if tag_objs:
                            obj.tags.set(tag_objs)

                # Reviews
                reviews = load_json('reviews')
                for r in reviews:
                    # простая вставка — без связи с пользователями
                    Review.objects.update_or_create(pk=r.get('pk'), defaults={
                        'name': r.get('name'),
                        'email': r.get('email'),
                        'message': r.get('message'),
                        'is_approved': r.get('is_approved', False),
                        'created_at': r.get('created_at'),
                    })
                    report['imported'].setdefault('reviews', 0)
                    report['imported']['reviews'] += 1

                # Site settings
                ss = load_json('site_settings')
                if ss:
                    try:
                        SiteSettings.objects.all().delete()
                        SiteSettings.objects.create(**ss)
                        report['imported']['site_settings'] = 1
                    except Exception:
                        pass

            # 3) копируем медиадир (перезаписывая файлы)
            media_src = tmpdir_p / 'media'
            if media_src.exists():
                for root, dirs, files in os.walk(media_src):
                    for f in files:
                        src = Path(root) / f
                        rel = src.relative_to(media_src)
                        dst = MEDIA_ROOT / rel
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        with open(src, 'rb') as rf, open(dst, 'wb') as wf:
                            wf.write(rf.read())
                        report['files'].append(str(rel))

            messages.success(request, 'Восстановление завершено')
            return render(request, 'backup/report.html', {'report': report})
        finally:
            # cleanup tmpdir
            try:
                import shutil

                shutil.rmtree(tmpdir)
            except Exception:
                pass

    return render(request, 'backup/restore.html', {'report': report})
