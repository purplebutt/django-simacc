from django.contrib import admin
from .models import Profile, User


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'company', 'created')
    readonly_fields = ('user', 'created', 'modified', 'slug')
    list_filter = ('gender',)
    ordering = ('-created',)
