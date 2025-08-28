from django.shortcuts import render
from django.db.models import Count, Q
from tours.models import Tour
from services.models import Service
from core.models import Category, Tag


def price_list(request):
    # Основные цены: берем price_adult как главную для туров/услуг
    tours = (
        Tour.objects.filter(is_active=True)
        .only('id', 'title', 'slug', 'price_adult')
        .order_by('-is_popular', '-created_at')
    )
    services = (
        Service.objects.filter(is_active=True)
        .only('id', 'title', 'slug', 'price_adult')
        .order_by('-created_at')
    )

    # Сайдбар: категории и теги
    # Категории для туров: аннотируем количеством активных туров
    rel_name_tours = Tour._meta.get_field('category').remote_field.related_name or 'tour_set'
    count_expr_tours = Count(rel_name_tours, filter=Q(**{f"{rel_name_tours}__is_active": True}))
    categories_tours = Category.objects.annotate(items=count_expr_tours).order_by('name')

    # Категории для услуг: related_name 'services'
    rel_name_services = Service._meta.get_field('category').remote_field.related_name or 'service_set'
    count_expr_services = Count(rel_name_services, filter=Q(**{f"{rel_name_services}__is_active": True}))
    categories_services = Category.objects.annotate(items=count_expr_services).order_by('name')

    tags = Tag.objects.order_by('name')

    # Популярные
    popular_tours = (
        Tour.objects.filter(is_active=True, is_popular=True)
        .order_by('-rating', '-created_at')[:6]
    )
    if not popular_tours:
        popular_tours = Tour.objects.filter(is_active=True).order_by('-rating', '-created_at')[:6]

    popular_services = (
        Service.objects.filter(is_active=True).order_by('-created_at')[:6]
    )

    # Импорт модели локально, чтобы не вызывать загрузку моделей при импорте модуля urls
    from .models import PricePDF

    # Актуальный PDF для скачивания (первый активный либо последний загруженный)
    pdf = PricePDF.objects.filter(is_active=True).first()
    if not pdf:
        pdf = PricePDF.objects.order_by('-uploaded_at').first()

    return render(request, 'prices/price_list.html', {
        'tours': tours,
        'services': services,
        'categories_tours': categories_tours,
        'categories_services': categories_services,
        'tags': tags,
        'popular_tours': popular_tours,
    'popular_services': popular_services,
    'price_pdf': pdf,
    })
