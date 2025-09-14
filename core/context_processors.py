from .models import SiteSettings
from tours.models import TourCategory
from services.models import ServiceCategory
from django.db.models import Count, Q

def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
    except Exception:
        settings = None
    return {'site_settings': settings}

def navigation_categories(request):
    """Добавляет категории туров и услуг для навигации"""
    # Родительские категории туров с количеством туров
    tour_categories = TourCategory.objects.filter(
        parent__isnull=True
    ).annotate(
        tours_count=Count('tours', filter=Q(tours__is_active=True))
    ).filter(tours_count__gt=0).order_by('name')
    
    # Родительские категории услуг с количеством услуг
    service_categories = ServiceCategory.objects.filter(
        parent__isnull=True
    ).annotate(
        services_count=Count('services', filter=Q(services__is_active=True))
    ).filter(services_count__gt=0).order_by('name')
    
    return {
        'nav_tour_categories': tour_categories,
        'nav_service_categories': service_categories,
    }

def active_page(request):
    """Определяет активную страницу для меню"""
    path = request.path
    
    # Определяем активную страницу по URL
    if path == '/':
        return {'active_page': 'home'}
    elif path.startswith('/tours/'):
        return {'active_page': 'tours'}
    elif path.startswith('/services/'):
        return {'active_page': 'services'}
    elif path.startswith('/prices/'):
        return {'active_page': 'prices'}
    elif path.startswith('/blog/'):
        return {'active_page': 'blog'}
    elif path.startswith('/reviews/'):
        return {'active_page': 'reviews'}
    else:
        return {'active_page': None}
