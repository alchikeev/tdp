from django.db import models
from django.urls import reverse

class Service(models.Model):
    title        = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True)

    # общие таксономии из core
    categories   = models.ManyToManyField(
        'services.ServiceCategory', blank=True,
        related_name='services', verbose_name='Категории услуг'
    )
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
    
    # Старые цены для скидок
    price_old_adult = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_old_child = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Дополнительная информация
    included = models.TextField("Что включено", blank=True, help_text="Список того, что включено в услугу")
    excluded = models.TextField("Что не включено", blank=True, help_text="Список того, что не включено в услугу")
    note_price = models.TextField("Примечание к цене", blank=True, help_text="Дополнительная информация о ценах")
    info = models.TextField("Полезная информация", blank=True, help_text="Важная информация для клиентов")
    
    # Рейтинг/метки
    rating = models.DecimalField(
        "Рейтинг",
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="0.00–5.00",
    )
    reviews_count = models.PositiveIntegerField("Кол-во отзывов", default=0)
    is_popular = models.BooleanField("Популярное", default=False)

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
    
    @property
    def has_discount(self) -> bool:
        return bool(self.price_old_adult and self.price_old_adult > self.price_adult)
class ServiceCategory(models.Model):
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("Слаг", unique=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        related_name='children', on_delete=models.CASCADE,
        verbose_name="Родительская категория"
    )

    class Meta:
        verbose_name = 'Категория услуги'
        verbose_name_plural = 'Категории услуг'

    def __str__(self):
        return self.name


class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image   = models.ImageField(upload_to='services/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.service.title} #{self.id}"
