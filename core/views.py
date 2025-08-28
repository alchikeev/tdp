from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from .models import Lead
from tours.models import Tour
from services.models import Service


def home(request):
    """Главная страница: отдаёт список актуальных туров для карточек на главной."""
    # Для главной берём до 9 случайных актуальных записей
    tours = list(Tour.objects.filter(is_active=True))
    services = list(Service.objects.filter(is_active=True))
    import random
    random.shuffle(tours)
    random.shuffle(services)
    tours = tours[:9]
    services = services[:9]
    return render(request, 'index.html', {'tours': tours, 'services': services})


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
