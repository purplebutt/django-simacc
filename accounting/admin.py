from django.contrib import admin
from .models import COA, COH, Company


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

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'address')
    list_filter = ('name','business_type')
    ordering = ('-created',)