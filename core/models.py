from django.db import models

class SiteSettings(models.Model):
    site_name   = models.CharField(max_length=160, default="TravelWorld")
    phone       = models.CharField(max_length=64, blank=True)
    phone_alt   = models.CharField(max_length=64, blank=True)
    email       = models.EmailField(blank=True)
    address     = models.CharField(max_length=255, blank=True)
    whatsapp    = models.URLField(blank=True)
    telegram    = models.URLField(blank=True)
    instagram   = models.URLField(blank=True)
    about_short = models.TextField(blank=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Глобальные настройки"

# Category model removed - not used in the application

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self): return self.name

class Lead(models.Model):
    created_at   = models.DateTimeField(auto_now_add=True)
    name         = models.CharField(max_length=120)
    phone        = models.CharField(max_length=32)
    email        = models.EmailField(blank=True)
    message      = models.TextField(blank=True)
    source_page  = models.URLField(max_length=600, blank=True)
    cta          = models.CharField(max_length=160, blank=True)
    # UTM
    utm_source   = models.CharField(max_length=100, blank=True)
    utm_medium   = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    utm_term     = models.CharField(max_length=100, blank=True)
    utm_content  = models.CharField(max_length=100, blank=True)
    # привязка к объекту (позже будем передавать tour/service)
    related_type = models.CharField(max_length=20, blank=True, choices=[("tour","tour"),("service","service")])
    related_id   = models.PositiveIntegerField(null=True, blank=True)
    status       = models.CharField(max_length=20, default="new",
                                    choices=[("new","new"),("sent","sent"),("error","error"),("done","done")])

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d} {self.name} / {self.phone}"
