from django.contrib import admin
from .models import Service, ServiceImage, ServiceCategory

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price_adult', 'price_child', 'price_extra', 'is_active', 'created_at')
    list_filter  = ('is_active', 'category', 'tags')
    search_fields = ('title', 'short_desc', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceImageInline]
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'tags', 'short_desc', 'description', 'location', 'cover')}),
        ('Цены', {'fields': ('price_adult', 'price_child', 'price_extra')}),
        ('SEO', {'fields': ('meta_title', 'meta_desc')}),
        ('Параметры', {'fields': ('is_active',)}),
    )

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
