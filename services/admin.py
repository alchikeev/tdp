from django.contrib import admin
from .models import Service, ServiceImage, ServiceCategory

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_categories', 'price_adult', 'price_child', 'price_extra', 'is_active', 'is_popular', 'rating', 'reviews_count', 'created_at')
    list_filter  = ('is_active', 'is_popular', 'categories', 'tags')
    search_fields = ('title', 'short_desc', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceImageInline]
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'categories', 'tags', 'short_desc', 'description', 'location', 'youtube_url', 'cover')}),
        ('Цены', {'fields': ('price_adult', 'price_child', 'price_extra', 'price_old_adult', 'price_old_child', 'note_price')}),
        ('Дополнительная информация', {'fields': ('included', 'excluded', 'info')}),
        ('SEO', {'fields': ('meta_title', 'meta_desc')}),
        ('Параметры', {'fields': ('is_active', 'is_popular', 'rating', 'reviews_count')}),
    )

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = 'Категории'

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
