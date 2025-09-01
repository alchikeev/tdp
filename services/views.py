from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count

from .models import Service, ServiceCategory
from core.models import Tag


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (по образцу tours.views)
# =========================
def _apply_filters_and_sort(request, qs):
    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(short_desc__icontains=q)
            | Q(description__icontains=q)
            | Q(location__icontains=q)
        )

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        qs = qs.filter(price_adult__gte=price_min)
    if price_max:
        qs = qs.filter(price_adult__lte=price_max)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        qs = qs.order_by('price_adult', '-created_at')
    elif sort == 'price_desc':
        qs = qs.order_by('-price_adult', '-created_at')
    elif sort == 'newest':
        qs = qs.order_by('-created_at')
    else:
        qs = qs.order_by('-created_at')

    return qs


def _sidebar_context():
    rel_name = Service._meta.get_field('categories').remote_field.related_name or 'service_set'
    count_expr = Count(rel_name, filter=Q(**{f"{rel_name}__is_active": True}))

    categories = ServiceCategory.objects.annotate(items=count_expr).order_by('name')
    tags = Tag.objects.order_by('name')

    # Популярные: безопасно проверяем наличие поля is_popular в модели
    field_names = {f.name for f in Service._meta.get_fields()}
    if 'is_popular' in field_names:
        popular = (
            Service.objects.filter(is_active=True, is_popular=True)
            .prefetch_related('categories', 'tags')
            .order_by('-created_at')[:6]
        )
    else:
        popular = (
            Service.objects.filter(is_active=True)
            .prefetch_related('categories', 'tags')
            .order_by('-created_at')[:6]
        )

    return categories, tags, popular


def _render_list(request, qs, extra_ctx=None):
    qs = _apply_filters_and_sort(request, qs)
    categories, tags, popular = _sidebar_context()

    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    ctx = {
        'services': page_obj.object_list,
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'popular_services': popular,
    }
    if extra_ctx:
        ctx.update(extra_ctx)

    return render(request, 'services/service_list.html', ctx)


# ==========
# ВЬЮХИ
# ==========
def service_list(request):
    qs = (
        Service.objects.filter(is_active=True)
        .prefetch_related('categories', 'tags')
    )
    return _render_list(request, qs)


def service_list_by_category(request, slug):
    category = get_object_or_404(ServiceCategory, slug=slug)
    qs = (
        Service.objects.filter(is_active=True, categories=category)
        .prefetch_related('categories', 'tags')
    )
    return _render_list(request, qs, extra_ctx={'active_category': category})


def service_list_by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    qs = (
        Service.objects.filter(is_active=True, tags=tag)
        .prefetch_related('categories', 'tags')
    )
    return _render_list(request, qs, extra_ctx={'active_tag': tag})


def service_detail(request, slug):
    service = get_object_or_404(Service.objects.prefetch_related('categories', 'tags', 'images'), slug=slug, is_active=True)

    # Похожие услуги по любой из категорий текущей услуги
    related = (
        Service.objects.filter(is_active=True, categories__in=service.categories.all())
        .exclude(id=service.id)
        .prefetch_related('categories', 'tags')
        .order_by('-created_at')[:6]
    )

    categories, tags, popular = _sidebar_context()

    ctx = {
        'service': service,
        'related': related,
        'categories': categories,
        'tags': tags,
        'popular_services': popular,
    }
    return render(request, 'services/service_detail.html', ctx)
