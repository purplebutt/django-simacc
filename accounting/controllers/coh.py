from django.db import models
from django.template.defaultfilters import slugify
from .base import AccModelBase
from django.contrib.auth.models import User


class COH(AccModelBase):
    # class fields
    _img_path = 'images/accounting/coh/'
    _img_def_path = 'images/default/coh.png'
    _account_group = [
        (1, 'ASSET'),
        (2, 'LIABILITY'),
        (3, 'EQUITY'),
        (4, 'REVENUE'),
        (5, 'EXPENSE'),
        (6, 'GAIN'),
        (7, 'LOSES'),
        (9, 'OTHER'),
    ] 
    _reports = [
        ('bs', 'BALANCE SHEET'),
        ('es', 'EQUITY STATEMENT'),
        ('pl', 'PROFIT & LOSS'),
        ('hp', 'HELPER/NO-REPORT'),
    ]

    # database fields
    number = models.IntegerField(unique=True)
    name = models.CharField(verbose_name="account header",max_length=125, unique=True)
    report = models.CharField(max_length=2, choices=_reports)
    group = models.IntegerField("account group", choices=_account_group)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='coh_authors', related_query_name='coh_author')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='coh_editors', related_query_name='coh_editor')

    class Meta:
        ordering = ('number',)
        verbose_name = "COH"
        verbose_name_plural = "COH"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(type(self), self).super(*args, **kwargs)

    def group_str(self):
        return tuple(filter(lambda x: x[0] == self.group, type(self)._account_group))[0][1]

    def report_str(self):
        return tuple(filter(lambda x: x[0] == self.report, type(self)._reports))[0][1]

    # class methods
    @classmethod
    def get_group_int(cls, key:str) -> int:
        x = filter(lambda x: x[1].lower()==key.lower(), cls._account_group)
        x = set(x)
        return int(x.pop()[0])
