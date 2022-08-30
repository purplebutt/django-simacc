from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse


#! Model Managers
class ModelManager(models.Manager):
    def get_queryset(self):
        result = super(type(self), self).get_queryset()
        return result

class InactiveManager(models.Manager):
    def get_queryset(self):
        result = super(type(self), self).get_queryset().filter(is_active=False)
        return result

class ActiveManager(models.Manager):
    def get_queryset(self):
        result = super(type(self), self).get_queryset().order_by('-created').filter(is_active=True)
        return result


#! Journal Entry/ General Journal 
class AccModelBase(models.Model):
    # class field
    app_name = 'accounting'

    # database model field
    slug = models.SlugField(max_length=125, unique=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # queryset
    objects = ModelManager()
    actives = ActiveManager()
    inactives = InactiveManager()

    class Meta:
        abstract = True
        ordering = ('-created',)

    # instance methods
    def get_absolute_url(self):
        return reverse(f'{type(self).app_name}:{type(self).__name__.lower()}_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse(f'{type(self).app_name}:{type(self).__name__.lower()}_update', kwargs={'slug': self.slug})

    def get_tablerow_style(self):
        pass

    # class methods
    @classmethod
    def get_add_url(cls):
        return reverse(f'{cls.app_name}:{cls.__name__.lower()}_add')

    @classmethod
    def get_search_url(cls):
        return reverse(f'{cls.app_name}:{cls.__name__.lower()}_search')

    @classmethod
    def get_list_url(cls):
        return reverse(f'{cls.app_name}:{cls.__name__.lower()}_list')
