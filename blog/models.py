from django.db import models
from django.urls import reverse


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    cover = models.ImageField(upload_to='blog/covers/', blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Статья'
        verbose_name_plural = 'Блог'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', args=[self.slug])
