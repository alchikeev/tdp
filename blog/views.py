from django.shortcuts import render, get_object_or_404
from .models import BlogPost


def list_view(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, 'blog/list.html', {'posts': posts})


def detail_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, 'blog/detail.html', {'post': post})
