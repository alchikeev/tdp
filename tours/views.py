from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count

from .models import Tour, TourCategory
from core.models import Tag


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================
def _apply_filters_and_sort(request, qs):
    """
    Применяет поиск (q), ценовые фильтры (price_min/price_max) и сортировку (sort) к QuerySet туров.
    Ожидаемые поля у Tour: title, short_desc, description, location, price_adult, created_at, is_popular.
    """
    # Поиск
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(short_desc__icontains=q)
            | Q(description__icontains=q)
            | Q(location__icontains=q)
        )

    # Цена
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    if price_min:
        qs = qs.filter(price_adult__gte=price_min)
    if price_max:
        qs = qs.filter(price_adult__lte=price_max)

    # Сортировка
    sort = request.GET.get("sort")
    if sort == "price_asc":
        qs = qs.order_by("price_adult", "-is_popular", "-created_at")
    elif sort == "price_desc":
        qs = qs.order_by("-price_adult", "-is_popular", "-created_at")
    elif sort == "newest":
        qs = qs.order_by("-created_at")
    else:
        # По умолчанию: сначала популярные, потом новые
        qs = qs.order_by("-is_popular", "-created_at")

    return qs


def _sidebar_context():
    """
    Данные для сайдбара: категории с количеством активных туров, теги (просто список),
    и блок «популярных» туров (если пусто — отдаем просто топ по рейтингу/дате).
    ВАЖНО: related_name у ForeignKey(Tour.category) может отличаться.
    Мы определяем его динамически и безопасно формируем Count/Q.
    """
    # Определяем related_name для Category -> Tour (или используем 'tour_set')
    rel_name = Tour._meta.get_field("category").remote_field.related_name or "tour_set"

    # Пример: Count("tours", filter=Q(tours__is_active=True))  # если related_name='tours'
    # Мы собираем ключи динамически:
    count_expr = Count(rel_name, filter=Q(**{f"{rel_name}__is_active": True}))

    categories = TourCategory.objects.annotate(items=count_expr).order_by("name")
    tags = Tag.objects.order_by("name")

    popular = (
        Tour.objects.filter(is_active=True, is_popular=True)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-rating", "-created_at")[:6]
    )
    if not popular:
        popular = (
            Tour.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-rating", "-created_at")[:6]
        )

    return categories, tags, popular


def _render_list(request, qs, extra_ctx=None):
    """
    Общий рендер листинга туров с пагинацией и данными сайдбара.
    """
    qs = _apply_filters_and_sort(request, qs)
    categories, tags, popular = _sidebar_context()

    # Пагинация
    paginator = Paginator(qs, 12)  # 12 карточек на страницу
    page_number = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    ctx = {
        "tours": page_obj.object_list,
        "page_obj": page_obj,
        "categories": categories,
        "tags": tags,
        "popular_tours": popular,
    }
    if extra_ctx:
        ctx.update(extra_ctx)

    return render(request, "tours/tour_list.html", ctx)


# ==========
# ВЬЮХИ
# ==========
def tour_list(request):
    """
    Список всех активных туров.
    """
    qs = (
        Tour.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("tags")
    )
    return _render_list(request, qs)


def tour_list_by_category(request, slug):
    """
    Список активных туров по категории.
    """
    category = get_object_or_404(TourCategory, slug=slug)
    qs = (
        Tour.objects.filter(is_active=True, category=category)
        .select_related("category")
        .prefetch_related("tags")
    )
    return _render_list(request, qs, extra_ctx={"active_category": category})


def tour_list_by_tag(request, slug):
    """
    Список активных туров по тегу.
    """
    tag = get_object_or_404(Tag, slug=slug)
    qs = (
        Tour.objects.filter(is_active=True, tags=tag)
        .select_related("category")
        .prefetch_related("tags")
    )
    return _render_list(request, qs, extra_ctx={"active_tag": tag})


def tour_detail(request, slug):
    """
    Детальная страница тура.
    """
    tour = get_object_or_404(
        Tour.objects.select_related("category").prefetch_related("tags"),
        slug=slug,
        is_active=True,
    )

    # Похожие туры из той же категории
    related = (
        Tour.objects.filter(is_active=True, category=tour.category)
        .exclude(id=tour.id)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-is_popular", "-created_at")[:6]
    )

    # Данные сайдбара
    categories, tags, popular = _sidebar_context()

    ctx = {
        "tour": tour,
        "related_tours": related,
        "categories": categories,
        "tags": tags,
        "popular_tours": popular,
        # Если используешь галерею/вложения через GenericFK — можно добавить:
        # "gallery_images": gallery_images,
        # "attachments": attachments,
    }
    return render(request, "tours/tour_detail.html", ctx)
