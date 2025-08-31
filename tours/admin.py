from django.contrib import admin
from .models import Tour, TourImage

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'price_adult', 'price_child', 'price_extra', 'is_active', 'is_popular', 'rating', 'reviews_count', 'created_at'
    )
    list_filter  = ('is_active', 'is_popular', 'category', 'tags')
    inlines = (TourImageInline,)
    fieldsets = (
        (None, {'fields': ('title','slug','category','tags','short_desc','description','duration','location','youtube_url','cover')}),
        ('Цены', {'fields': ('price_adult','price_child','price_extra','price_old_adult','price_old_child')}),
        ('SEO', {'fields': ('meta_title','meta_desc')}),
        ('Видимость', {'fields': ('is_active','is_popular','rating','reviews_count')}),
    )
