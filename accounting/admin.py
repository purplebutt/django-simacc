from django.contrib import admin
from .models import COA, COH


@admin.register(COA)
class COAAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'is_active')
    list_filter = ('normal','header')
    ordering = ('number',)

@admin.register(COH)
class COHAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'is_active')
    list_filter = ('group',)
    ordering = ('number',)
