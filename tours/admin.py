from django.contrib import admin
from .models import Tour, TourImage, TourCategory

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'get_categories', 'price_adult', 'price_child', 'price_extra', 'is_active', 'is_popular', 'rating', 'reviews_count', 'created_at'
    )
    list_filter  = ('is_active', 'is_popular', 'categories', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    inlines = (TourImageInline,)
    fieldsets = (
        (None, {'fields': ('title','slug','categories','tags','short_desc','description','duration','location','youtube_url','cover')}),
        ('Цены', {'fields': ('price_adult','price_child','price_extra','price_old_adult','price_old_child')}),
        ('SEO', {'fields': ('meta_title','meta_desc')}),
        ('Видимость', {'fields': ('is_active','is_popular','rating','reviews_count')}),
    )
    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = 'Категории'

@admin.register(TourCategory)
class TourCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {'slug': ('name',)}
