from django.contrib import admin
from .models import Company

# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'address')
    list_filter = ('name','business_type')
    ordering = ('-created',)