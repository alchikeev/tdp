from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Service            # проверь имя модели/поля
from core.models import Category, Tag  # поправь импорт, если они в другом app

def _paginate(request, qs, per_page=12):
    page = request.GET.get('page')
    return Paginator(qs, per_page).get_page(page)

def service_list(request):
    qs = Service.objects.filter(is_active=True).select_related('category').prefetch_related('tags')
    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(short_desc__icontains=q) | Q(description__icontains=q))

    # Пагинация
    page_obj = _paginate(request, qs.order_by('-created_at') if hasattr(Service, 'created_at') else qs.order_by('-id'))

    # Подготовка контекста для сайдбара
    categories = Category.objects.all().order_by('name')
    # подсчитать количество услуг в категории (если related_name 'services' присутствует)
    # добавим атрибут items для шаблона, безопасно пропуская, если нет связи
    cats_with_counts = []
    for c in categories:
        try:
            c.items = c.services.filter(is_active=True).count()
        except Exception:
            c.items = None
        cats_with_counts.append(c)

    tags = Tag.objects.all().order_by('name')

    # Популярные: если в модели есть поле 'is_popular' — использовать его, иначе взять последние 5 активных
    popular_qs = None
    if hasattr(Service, 'is_popular'):
        popular_qs = Service.objects.filter(is_active=True, is_popular=True).order_by('-created_at')
    else:
        popular_qs = Service.objects.filter(is_active=True).order_by('-created_at')
    popular_services = list(popular_qs[:5])

    return render(request, 'services/service_list.html', {
        'services': page_obj.object_list,
        'page_obj': page_obj,
        'categories': cats_with_counts,
        'tags': tags,
        'popular_services': popular_services,
    })

def service_list_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    qs = Service.objects.filter(is_active=True, category=category)
    page_obj = _paginate(request, qs.order_by('-id'))
    return render(request, 'services/service_list.html', {
        'services': page_obj.object_list,
        'page_obj': page_obj,
        'categories': Category.objects.all().order_by('name'),
        'tags': Tag.objects.all().order_by('name'),
        'active_category': category,
    })

def service_list_by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    qs = Service.objects.filter(is_active=True, tags=tag)
    page_obj = _paginate(request, qs.order_by('-id'))
    return render(request, 'services/service_list.html', {
        'services': page_obj.object_list,
        'page_obj': page_obj,
        'categories': Category.objects.all().order_by('name'),
        'tags': Tag.objects.all().order_by('name'),
        'active_tag': tag,
    })

def service_detail(request, slug):
    service = get_object_or_404(Service.objects.select_related('category').prefetch_related('tags', 'images'), slug=slug, is_active=True)

    # Похожие услуги из той же категории
    related = (
        Service.objects.filter(is_active=True, category=service.category)
        .exclude(id=service.id)
        .select_related('category')
        .prefetch_related('tags')
        .order_by('-created_at')[:6]
    )

    # Сайдбар: категории с подсчётом, теги и популярные
    categories = Category.objects.all().order_by('name')
    cats_with_counts = []
    for c in categories:
        try:
            c.items = c.services.filter(is_active=True).count()
        except Exception:
            c.items = None
        cats_with_counts.append(c)

    tags = Tag.objects.all().order_by('name')

    if hasattr(Service, 'is_popular'):
        popular_qs = Service.objects.filter(is_active=True, is_popular=True).order_by('-created_at')
    else:
        popular_qs = Service.objects.filter(is_active=True).order_by('-created_at')
    popular_services = list(popular_qs[:5])

    ctx = {
        'service': service,
        'related': related,
        'categories': cats_with_counts,
        'tags': tags,
        'popular_services': popular_services,
    }
    return render(request, 'services/service_detail.html', ctx)
