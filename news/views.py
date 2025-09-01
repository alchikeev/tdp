from django.shortcuts import render, get_object_or_404
from .models import NewsPost


def list_view(request):
    posts = NewsPost.objects.filter(is_published=True)
    return render(request, 'news/list.html', {'posts': posts})


def detail_view(request, slug):
    post = get_object_or_404(NewsPost, slug=slug, is_published=True)
    return render(request, 'news/detail.html', {'post': post})
