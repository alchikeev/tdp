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
    page_obj = _paginate(request, qs.order_by('-created_at') if hasattr(Service, 'created_at') else qs.order_by('-id'))
    return render(request, 'services/service_list.html', {
        'services': page_obj.object_list,
        'page_obj': page_obj,
        'categories': Category.objects.all().order_by('name'),
        'tags': Tag.objects.all().order_by('name'),
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
    service = get_object_or_404(Service, slug=slug, is_active=True)
    return render(request, 'services/service_detail.html', {'service': service})
