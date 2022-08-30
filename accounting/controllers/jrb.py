from django.db import models
from django.db.models import Case, When, Sum, Count, F
from django.template.defaultfilters import slugify
from .base import AccModelBase
from django.contrib.auth.models import User


class JRBManager(models.Manager):
    def get_queryset(self):
        result = super(type(self), self).get_queryset().filter(is_active=True).annotate(
            balance=Sum(Case(
                When(journal__group='d', then=F('journal__amount')),
                When(journal__group='c', then=F('journal__amount')*-1),
                default=0,
            )),
            entries=Count('journal')
        )
        return result


class JRB(AccModelBase):
    # helper functions
    def number_validator(value:str):
        if JRB.objects.filter(number=value.lower()).exists():
            raise ValidationError(
                f"Duplicate value: {value}, this field should be unique..!"
            ) 

    # class fields
    _img_path = 'images/jrb/'
    _img_def_path = 'images/default/jrb.png'

    # database fields
    number = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=125)
    group = models.CharField(verbose_name="type",max_length=125)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='jrb_authors', related_query_name='jrb_author')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='jrb_editors', related_query_name='jrb_editor')

    objects = JRBManager()

    class Meta:
        verbose_name = "JRB"
        verbose_name_plural = "JRB"

    # instance methods
    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        self.slug = slugify(self.number)
        self.number = self.number.lower()
        self.group = self.group.upper()
        super(type(self), self).save(*args, **kwargs)

    def get_tablerow_style(self):
        x = type(self).objects.filter(pk=self.pk).first().balance
        if x != 0:
            return "table-warning"
        else:
            return "table-info"
