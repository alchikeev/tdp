from .models import SiteSettings

def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
    except Exception:
        settings = None
    return {'site_settings': settings}

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
