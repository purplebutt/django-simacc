from django.db import models
from django.template.defaultfilters import slugify
from .base import AccModelBase
from django.contrib.auth.models import User
from .coh import COH


class COA(AccModelBase):
    _img_path = 'images/accounting/coa/'
    _img_def_path = 'images/default/coa.png'
    _normal_balance = [
        ('d', 'DEBIT'),
        ('c', 'CREDIT'),
    ]
    number = models.FloatField(unique=True)
    name = models.CharField(verbose_name="account name",max_length=125, unique=True)
    normal = models.CharField(verbose_name="normal balance", max_length=1, choices=_normal_balance)
    header = models.ForeignKey(COH, verbose_name="account header", on_delete=models.RESTRICT, limit_choices_to={'is_active':True}, 
        related_name='accounts', related_query_name='account')
    is_cashflow = models.BooleanField("is cash flow", default=False)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='coa_authors', related_query_name='coa_author')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='coa_editors', related_query_name='coa_editor')

    class Meta:
        ordering = ('number',)
        verbose_name = "COA"
        verbose_name_plural = "COA"

    # instance methods
    @property
    def is_pnl(self)->bool:
        """
        return True if account report is "PROFIT & LOSS" otherwise return False
        """
        return self.report() == "PROFIT & LOSS"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(type(self), self).save(*args, **kwargs)

    def group(self):
        return self.header.group_str()

    def report(self):
        return self.header.report_str()

    # class methods
    @classmethod
    def get_with_number(cls, sep:str=" "):
        result = map(lambda i: str(i[0])+sep+i[1], cls.actives.values_list('number', 'name'))
        return result
