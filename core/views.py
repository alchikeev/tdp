from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.template.loader import render_to_string
from .models import Lead
from tours.models import Tour, TourCategory
from services.models import Service
from reviews.models import Review
from news.models import NewsPost
from blog.models import BlogPost


def home(request):
    """Главная страница: отдаёт список актуальных туров для карточек на главной."""
    # Для главной берём 6 случайных актуальных туров
    tours = list(Tour.objects.filter(is_active=True))
    services = list(Service.objects.filter(is_active=True))
    import random
    random.shuffle(tours)
    random.shuffle(services)
    tours = tours[:6]  # Изменено с 9 на 6
    services = services[:9]
    
    # Родительские категории туров с количеством туров
    parent_categories = TourCategory.objects.filter(
        parent__isnull=True
    ).annotate(
        tours_count=Count('tours', filter=Q(tours__is_active=True))
    ).filter(tours_count__gt=0).order_by('name')
    
    # Общее количество активных туров
    total_tours_count = Tour.objects.filter(is_active=True).count()
    
    # Случайные одобренные отзывы (макс. 3)
    reviews = list(Review.objects.filter(is_approved=True))
    random.shuffle(reviews)
    reviews = reviews[:3]
    # Последние три новости для главной страницы
    news_posts = list(NewsPost.objects.filter(is_published=True).order_by('-pub_date')[:3])
    # Случайные блог-посты (макс. 3)
    blog_list = list(BlogPost.objects.filter(is_published=True))
    random.shuffle(blog_list)
    blog_posts = blog_list[:3]
    return render(request, 'index.html', {
        'tours': tours,
        'services': services,
        'reviews': reviews,
        'news_posts': news_posts,
        'blog_posts': blog_posts,
        'parent_categories': parent_categories,
        'total_tours_count': total_tours_count,
    })


@require_POST
def lead_create(request):
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    if not (name and phone):
        return HttpResponseBadRequest('name and phone required')
    lead = Lead.objects.create(
        name=name,
        phone=phone,
        email=request.POST.get('email', ''),
        message=request.POST.get('message', ''),
        source_page=request.POST.get('source_page', request.META.get('HTTP_REFERER', '')),
        cta=request.POST.get('cta', ''),
        utm_source=request.POST.get('utm_source', ''),
        utm_medium=request.POST.get('utm_medium', ''),
        utm_campaign=request.POST.get('utm_campaign', ''),
        utm_term=request.POST.get('utm_term', ''),
        utm_content=request.POST.get('utm_content', ''),
        related_type=request.POST.get('related_type', ''),
        related_id=request.POST.get('related_id') or None,
    )
    return JsonResponse({'ok': True, 'id': lead.id})


def get_subcategories(request, category_id):
    """API endpoint для получения подкатегорий родительской категории."""
    parent_category = get_object_or_404(TourCategory, id=category_id, parent__isnull=True)
    
    # Получаем подкатегории с количеством туров
    subcategories = TourCategory.objects.filter(
        parent=parent_category
    ).annotate(
        tours_count=Count('tours', filter=Q(tours__is_active=True))
    ).filter(tours_count__gt=0).order_by('name')
    
    # Рендерим HTML для подкатегорий
    html = render_to_string('partials/subcategories.html', {
        'subcategories': subcategories
    })
    
    return JsonResponse({'html': html})


def get_tours_by_category(request, category_id):
    """API endpoint для получения туров по категории."""
    category = get_object_or_404(TourCategory, id=category_id)
    
    # Получаем туры этой категории (включая подкатегории)
    tours = Tour.objects.filter(
        categories=category,
        is_active=True
    ).select_related().prefetch_related('categories')
    
    # Случайно перемешиваем и берем до 6
    import random
    tours_list = list(tours)
    random.shuffle(tours_list)
    tours_list = tours_list[:6]
    
    # Формируем данные для JSON
    tours_data = []
    for tour in tours_list:
        tours_data.append({
            'id': tour.id,
            'title': tour.title,
            'location': tour.location,
            'cover': tour.cover.url if tour.cover else None,
            'url': tour.get_absolute_url(),
            'rating': float(tour.rating) if tour.rating else 4.5,
            'is_popular': tour.is_popular,
            'has_discount': tour.has_discount,
        })
    
    return JsonResponse({'tours': tours_data})


def get_all_tours(request):
    """API endpoint для получения всех туров."""
    tours = Tour.objects.filter(is_active=True).select_related().prefetch_related('categories')
    
    # Случайно перемешиваем и берем до 6
    import random
    tours_list = list(tours)
    random.shuffle(tours_list)
    tours_list = tours_list[:6]
    
    # Формируем данные для JSON
    tours_data = []
    for tour in tours_list:
        tours_data.append({
            'id': tour.id,
            'title': tour.title,
            'location': tour.location,
            'cover': tour.cover.url if tour.cover else None,
            'url': tour.get_absolute_url(),
            'rating': float(tour.rating) if tour.rating else 4.5,
            'is_popular': tour.is_popular,
            'has_discount': tour.has_discount,
        })
    
    return JsonResponse({'tours': tours_data})


def health_ok(request):
    """Health check endpoint для Docker healthcheck."""
    return HttpResponse("OK", status=200)
