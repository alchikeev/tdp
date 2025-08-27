from django.db import models
from django.urls import reverse

# Берём таксономии из core
# (если решишь разделить категории для туров и услуг — сделаем отдельные модели)
class Tour(models.Model):
    title        = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True)
    category     = models.ForeignKey('core.Category', on_delete=models.PROTECT, related_name='tours')
    tags         = models.ManyToManyField('core.Tag', blank=True, related_name='tours')

    short_desc   = models.TextField(blank=True)          # короткое описание для карточек
    description  = models.TextField()                    # полное описание
    duration     = models.CharField(max_length=80, blank=True)    # "3 дня / 2 ночи"
    location     = models.CharField(max_length=160, blank=True)   # Пхукет, Симилан и т.д.
    youtube_url  = models.URLField(blank=True)

    price_adult  = models.DecimalField(max_digits=10, decimal_places=2)
    price_child  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    price_old_adult = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_old_child = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating          = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # 4.9
    reviews_count   = models.PositiveIntegerField(default=0)
    is_popular      = models.BooleanField(default=False)

    cover        = models.ImageField(upload_to='tours/covers/', blank=True, null=True)  # обложка карточки
    is_active    = models.BooleanField(default=True)

    meta_title   = models.CharField(max_length=180, blank=True)
    meta_desc    = models.CharField(max_length=300, blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    @property
    def has_discount(self):
        return bool(self.price_old_adult and self.price_old_adult > self.price_adult)

    class Meta:
        ordering = ('-created_at', 'title')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tours:detail', kwargs={'slug': self.slug})


class TourImage(models.Model):
    tour   = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image  = models.ImageField(upload_to='tours/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.tour.title} #{self.id}"
