from django.views.generic import ListView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Review


class ReviewListView(ListView):
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        return Review.objects.filter(is_approved=True)


class ReviewCreateView(CreateView):
    model = Review
    fields = ['name', 'email', 'image', 'message']
    template_name = 'reviews/review_form.html'
    success_url = reverse_lazy('reviews:list')

    def form_valid(self, form):
        # Пользователь не обязателен, просто сохраняем отзыв
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Спасибо! Ваш отзыв отправлен и будет отображён после модерации."
        )
        return response
