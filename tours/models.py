# tours/models.py
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


# =========================
#  QuerySet / Manager
# =========================
class TourQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def popular(self):
        return self.active().filter(is_popular=True)

    def search(self, q: str):
        q = (q or "").strip()
        if not q:
            return self
        return self.filter(
            models.Q(title__icontains=q)
            | models.Q(short_desc__icontains=q)
            | models.Q(description__icontains=q)
            | models.Q(location__icontains=q)
        )


# =========================
#  Основные модели
# =========================
class Tour(models.Model):
    # Таксономии из core
    category = models.ForeignKey(
        "core.Category",
        on_delete=models.PROTECT,
        related_name="tours",
        verbose_name="Категория",
    )
    tags = models.ManyToManyField(
        "core.Tag",
        related_name="tours",
        blank=True,
        verbose_name="Теги",
    )

    # Базовые
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", unique=True, db_index=True)

    # Контент
    short_desc = models.TextField("Короткое описание", blank=True)
    description = models.TextField("Полное описание")
    duration = models.CharField("Длительность", max_length=80, blank=True)  # напр. "3 дня / 2 ночи"
    location = models.CharField("Локация", max_length=160, blank=True)
    youtube_url = models.URLField("YouTube-видео", blank=True)

    # Цены
    price_adult = models.DecimalField(
        "Цена взрослого",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    price_child = models.DecimalField(
        "Цена детская",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )

    # Дополнительные услуги: отдельная цена для опций/доплат
    price_extra = models.DecimalField(
        "Цена дополнительных услуг",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )

    price_old_adult = models.DecimalField(
        "Старая цена (взрослый)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    price_old_child = models.DecimalField(
        "Старая цена (детский)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )

    # Рейтинг/метки
    rating = models.DecimalField(
        "Рейтинг",
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("5"))],
        help_text="0.00–5.00",
    )
    reviews_count = models.PositiveIntegerField("Кол-во отзывов", default=0)
    is_popular = models.BooleanField("Популярное", default=False)
    is_active = models.BooleanField("Показывать на сайте", default=True)

    # Медиа
    cover = models.ImageField(
        "Обложка",
        upload_to="tours/covers/",
        blank=True,
        null=True,
    )

    # SEO
    meta_title = models.CharField("Meta title", max_length=180, blank=True)
    meta_desc = models.CharField("Meta description", max_length=300, blank=True)

    # Служебное
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    # Менеджер
    objects = TourQuerySet.as_manager()

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ("-created_at", "title")
        indexes = [
            models.Index(fields=["is_active", "-created_at"], name="tour_active_created_idx"),
            models.Index(fields=["slug"], name="tour_slug_idx"),
            models.Index(fields=["category", "is_active"], name="tour_category_active_idx"),
            models.Index(fields=["is_popular", "-created_at"], name="tour_popular_idx"),
        ]
        constraints = [
            # Старая цена (если задана) должна быть >= новой.
            models.CheckConstraint(
                name="tour_old_adult_ge_new",
                check=models.Q(price_old_adult__isnull=True) | models.Q(price_old_adult__gte=models.F("price_adult")),
            ),
            models.CheckConstraint(
                name="tour_old_child_ge_new",
                check=models.Q(price_old_child__isnull=True) | models.Q(price_old_child__gte=models.F("price_child")),
            ),
        ]

    def __str__(self) -> str:
        return self.title

    # ======= URLs =======
    def get_absolute_url(self) -> str:
        return reverse("tours:detail", kwargs={"slug": self.slug})

    # ======= Удобные свойства =======
    @property
    def has_discount(self) -> bool:
        return bool(self.price_old_adult and self.price_old_adult > self.price_adult)

    @property
    def discount_percent(self):
        """
        Скидка в процентах для взрослой цены (целое число), либо None.
        """
        if self.has_discount and self.price_adult:
            try:
                return int((self.price_old_adult - self.price_adult) / self.price_old_adult * 100)
            except Exception:
                return None
        return None

    @property
    def has_child_price(self) -> bool:
        return self.price_child is not None


class TourImage(models.Model):
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Тур",
    )
    image = models.ImageField("Изображение", upload_to="tours/gallery/")
    caption = models.CharField("Подпись", max_length=200, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Фото тура"
        verbose_name_plural = "Фото тура"
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["tour", "order"], name="tourimage_tour_order_idx"),
        ]
        constraints = [
            # Порядок неотрицателен
            models.CheckConstraint(
                name="tourimage_order_nonnegative",
                check=models.Q(order__gte=0),
            )
        ]

    def __str__(self) -> str:
        return f"{self.tour.title} #{self.pk}"
