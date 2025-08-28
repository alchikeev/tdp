from django.db import models
from django.conf import settings


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Необязательное поле для привязки к зарегистрированному пользователю'
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    message = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(
        upload_to='reviews/images/',
        blank=True,
        null=True,
        help_text='Необязательное изображение для отзыва'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.name}"
