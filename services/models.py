from django.db import models
from django.urls import reverse

class Service(models.Model):
    title        = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True)

    # общие таксономии из core
    category     = models.ForeignKey('core.Category', on_delete=models.PROTECT, related_name='services')
    tags         = models.ManyToManyField('core.Tag', blank=True, related_name='services')

    short_desc   = models.TextField(blank=True)
    description  = models.TextField()
    location     = models.CharField(max_length=160, blank=True)
    youtube_url  = models.URLField(blank=True)

    # цены как у туров (взрослый/детский)
    price_adult  = models.DecimalField(max_digits=10, decimal_places=2)
    price_child  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Дополнительные услуги — отдельная цена для опций
    price_extra  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    cover        = models.ImageField(upload_to='services/covers/', blank=True, null=True)
    is_active    = models.BooleanField(default=True)

    meta_title   = models.CharField(max_length=180, blank=True)
    meta_desc    = models.CharField(max_length=300, blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', 'title')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('services:detail', kwargs={'slug': self.slug})


class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image   = models.ImageField(upload_to='services/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.service.title} #{self.id}"
