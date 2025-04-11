from django.contrib import admin
from .models import Ad, ExchangeProposal, Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_category', 'condition', 'created_at', 'user')  # Поля, которые будут отображаться
    search_fields = ('title', 'description')
    list_filter = ('category', 'condition')
    ordering = ('-created_at',)

    def get_category(self, obj):
        return obj.category.name if obj.category else 'Нет категории'

    get_category.short_description = 'Категория'  # Указываем название колонки в списке


class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = ('ad_sender', 'ad_receiver', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('ad_sender__title', 'ad_receiver__title', 'comment')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(ExchangeProposal, ExchangeProposalAdmin)
