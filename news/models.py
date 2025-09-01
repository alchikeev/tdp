from django.db import models
from django.urls import reverse

class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    cover = models.ImageField(upload_to='news/covers/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:detail', args=[self.slug])
