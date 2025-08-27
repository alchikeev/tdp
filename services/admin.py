from django.contrib import admin
from .models import Service, ServiceImage

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price_adult', 'price_child', 'is_active', 'created_at')
    list_filter  = ('is_active', 'category', 'tags')
    search_fields = ('title', 'short_desc', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceImageInline]
