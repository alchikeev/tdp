from django.contrib import admin
from .models import SiteSettings, Category, Tag, Lead

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'phone', 'email')
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)
    list_filter = ('parent',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'phone', 'utm_source', 'status')
    list_filter  = ('status', 'utm_source')
    search_fields = ('name', 'phone', 'email', 'utm_campaign')
    readonly_fields = ('created_at',)
