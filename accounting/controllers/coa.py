from django.db import models
from django.template.defaultfilters import slugify
from django.db.models import Case, When, Sum, Count, F, Q
from .base import AccModelBase, ActiveManager, ModelManager
from django.contrib.auth.models import User
from ..models import COH
from datetime import date, timedelta
from django.utils import timezone


class COATBManager(models.Manager):
    def get_queryset(self):
        result = super(type(self), self).get_queryset().filter(is_active=True).annotate(
            debit=Sum(Case(
                When(journal__group='d', then=F('journal__amount')), default=0,
            )),
            credit=Sum(Case(
                When(journal__group='c', then=F('journal__amount')), default=0,
            )),
            balance=Sum(Case(
                When(journal__group='d', then=F('journal__amount')),
                When(journal__group='c', then=F('journal__amount')*-1),
                default=0,
            )),
            entries=Count('journal')
        )
        return result.filter(Q(balance__gt=0)|Q(balance__lt=0)).order_by('number')


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

    objects = ModelManager()
    trialbalance = COATBManager()

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

    @classmethod
    def get_tb_at(cls, period_from:date, period_to:date):
        result = cls.objects.annotate(
            previous=Sum(Case(
                When(Q(journal__group='d')&Q(journal__date__lt=period_from), then=F('journal__amount')),
                When(Q(journal__group='c')&Q(journal__date__lt=period_from), then=F('journal__amount')*-1),
                default=0,
            )),
            debit=Sum(Case(
                When(Q(journal__group='d')&Q(journal__date__gte=period_from)&Q(journal__date__lte=period_to), then=F('journal__amount')), default=0,
            )),
            credit=Sum(Case(
                When(Q(journal__group='c')&Q(journal__date__gte=period_from)&Q(journal__date__lte=period_to), then=F('journal__amount')), default=0,
            )),
            balance=Sum(Case(
                When(Q(journal__group='d')&Q(journal__date__lte=period_to), then=F('journal__amount')),
                When(Q(journal__group='c')&Q(journal__date__lte=period_to), then=F('journal__amount')*-1),
                default=0,
            )),
            entries=Count('journal')
        )
        # return result.filter(Q(balance__gt=0)).order_by('number')
        return result.exclude(Q(balance=0)&Q(previous=0)&Q(debit=0)&Q(credit=0)).order_by('number')
        # return result.filter(
        #     (Q(balance!=0)&Q(previous!=0)&Q(debit!=0)&Q(credit!=0))
        # ).order_by('number')
