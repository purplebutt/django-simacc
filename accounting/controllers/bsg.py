from django.db import models
from django.template.defaultfilters import slugify
from .base import AccModelBase
from django.contrib.auth.models import User


class BSG(AccModelBase):
    # class fields
    _img_path = 'images/bsg/'
    _img_def_path = 'images/default/bsg.png'

    # database fields
    number = models.FloatField(unique=True)
    name = models.CharField(verbose_name="account name",max_length=125, unique=True)
    group = models.CharField(verbose_name="type",max_length=125)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='bsg_authors', related_query_name='bsg_author')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='bsg_editors', related_query_name='bsg_editor')

    class Meta:
        ordering = ('number',)
        verbose_name = "BSG"
        verbose_name_plural = "BSG"

    # instance methods
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.group += self.group.upper()
        super(type(self), self).save(*args, **kwargs)
