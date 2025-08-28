from django.contrib import admin
from .models import PricePDF


@admin.register(PricePDF)
class PricePDFAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'uploaded_at')
    list_filter = ('is_active', 'uploaded_at')
    search_fields = ('name', 'file')
    actions = ['make_active']

    def make_active(self, request, queryset):
        # Снимаем флаг is_active у всех и ставим только выбранный
        queryset.update(is_active=False)
        # Пометим первый выбранный как активный
        first = queryset.first()
        if first:
            first.is_active = True
            first.save()
    make_active.short_description = 'Сделать выбранный прайс активным'
