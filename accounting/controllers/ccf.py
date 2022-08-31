from django.db import models
from django.template.defaultfilters import slugify
from .base import AccModelBase
from django.contrib.auth.models import User


class CCF(AccModelBase):
    # class fields
    _img_path = 'images/accounting/ccf/'
    _img_def_path = 'images/default/ccf.png'
    _flow = [
        ('i', 'INFLOW'),
        ('o', 'OUTFLOW'),
    ]
    _activities = [
        (1, 'OPERATING'),
        (2, 'INVESTING'),
        (3, 'FINANCING'),
        (4, 'OTHERS'),
    ]

    # database fields
    number = models.FloatField(unique=True)
    name = models.CharField(verbose_name="account name",max_length=125, unique=True)
    flow = models.CharField(max_length=1, choices=_flow)
    activity = models.IntegerField(choices=_activities)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='ccf_authors', related_query_name='ccf_author')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='ccf_editors', related_query_name='ccf_editor')

    class Meta:
        ordering = ('number',)
        verbose_name = "CCF"
        verbose_name_plural = "CCF"

    # instance methods
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(type(self), self).save(*args, **kwargs)

    def get_tablerow_style(self):
        if self.flow == 'i':
            return "table-info"
        else:
            return "table-warning"
