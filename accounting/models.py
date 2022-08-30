from django.db import models
from django.db.models import Q, F, Sum, When, Case, Count
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from media.api.manager import resize_image, delete_model_image
from .mybase import AccModelBase


#! Company
class Company(AccModelBase):
    _img_path = 'images/accounting/company/'
    _img_def_path = 'images/default/company.png'
    _legal = [
        ('ud','UD'),
        ('cv','CV'),
        ('pt','PT'),
        ('kp','Koperasi'),
        ('ys','Yayasan'),
        ('ot','Lainnya'),
    ]
    name = models.CharField(max_length=125, unique=True)
    legal = models.CharField(max_length=3, choices=_legal, default='ot')
    business_type = models.CharField(max_length=125)
    address = models.CharField(max_length=125)
    city = models.CharField(max_length=125)
    country = models.CharField(max_length=125)
    phone = models.CharField(max_length=25, blank=True)
    email = models.EmailField(max_length=64, unique=True)
    desc = models.TextField(blank=True)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'created_companys', related_query_name='created_company')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'edited_companys', related_query_name='edited_company')

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Company"

    def __repr__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        if settings.DEBUG:
            delete_model_image(self, Company, Company._img_def_path)
            super(Company, self).save(*args, **kwargs)
            resize_image(self.image.path)
        else:
            super(Company, self).save(*args, **kwargs)


#! COA header
class COH(AccModelBase):
    # class fields
    _img_path = 'images/COH/'
    _img_def_path = 'images/default/COH.png'
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
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'created_cohs', related_query_name='created_coh')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'edited_cohs', related_query_name='edited_coh')

    class Meta:
        ordering = ('number',)
        verbose_name = "COH"
        verbose_name_plural = "COH"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        if settings.DEBUG:
            delete_model_image(self, type(self), type(self)._img_def_path)
            super(type(self), self).save(*args, **kwargs)
            resize_image(self.image.path)
        else:
            super(type(self), self).save(*args, **kwargs)

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


#! Chart Of Account
class COA(AccModelBase):
    _img_path = 'images/COA/'
    _img_def_path = 'images/default/COA.png'
    _normal_balance = [
        ('d', 'DEBIT'),
        ('c', 'CREDIT'),
    ]
    number = models.FloatField(unique=True)
    name = models.CharField(verbose_name="account name",max_length=125, unique=True)
    normal = models.CharField(verbose_name="normal balance", max_length=1, choices=_normal_balance)
    header = models.ForeignKey(COH, verbose_name="account header", on_delete=models.RESTRICT, limit_choices_to={'is_active':True}, related_name='accounts', related_query_name='account')
    is_cashflow = models.BooleanField("is cash flow", default=False)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'created_coas', related_query_name='created_coa')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'edited_coas', related_query_name='edited_coa')

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

        if settings.DEBUG:
            delete_model_image(self, type(self), type(self)._img_def_path)
            super(type(self), self).save(*args, **kwargs)
            resize_image(self.image.path)
        else:
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


#! Chart Of Cash Flow
class CCF(AccModelBase):
    # class fields
    _img_path = 'images/CCF/'
    _img_def_path = 'images/default/CCF.png'
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
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'created_ccfs', related_query_name='created_ccf')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'edited_ccfs', related_query_name='edited_ccf')

    class Meta:
        ordering = ('number',)
        verbose_name = "CCF"
        verbose_name_plural = "CCF"

    # instance methods
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        if settings.DEBUG:
            delete_model_image(self, type(self), type(self)._img_def_path)
            super(type(self), self).save(*args, **kwargs)
            resize_image(self.image.path)
        else:
            super(type(self), self).save(*args, **kwargs)

    def get_tablerow_style(self):
        if self.flow == 'i':
            return "table-info"
        else:
            return "table-warning"


#! Business Segment
class BSG(AccModelBase):
    # class fields
    _img_path = 'images/BSG/'
    _img_def_path = 'images/default/BSG.png'

    # database fields
    number = models.FloatField(unique=True)
    name = models.CharField(verbose_name="account name",max_length=125, unique=True)
    group = models.CharField(verbose_name="type",max_length=125)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'created_bsgs', related_query_name='created_bsg')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'edited_bsgs', related_query_name='edited_bsg')

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

        if settings.DEBUG:
            delete_model_image(self, type(self), type(self)._img_def_path)
            super(type(self), self).save(*args, **kwargs)
            resize_image(self.image.path)
        else:
            super(type(self), self).save(*args, **kwargs)


#! Journal Batch 
class JRBManager(models.Manager):
    def get_queryset(self):
        c = JRE()
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
    _img_path = 'images/JRB/'
    _img_def_path = 'images/default/JRB.png'

    # database fields
    number = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=125)
    group = models.CharField(verbose_name="type",max_length=125)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'created_jrbs', related_query_name='created_jrb')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'edited_jrbs', related_query_name='edited_jrb')

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

        if settings.DEBUG:
            delete_model_image(self, type(self), type(self)._img_def_path)
            super(type(self), self).save(*args, **kwargs)
            resize_image(self.image.path)
        else:
            super(type(self), self).save(*args, **kwargs)

    def get_tablerow_style(self):
        x = type(self).objects.filter(pk=self.pk).first().balance
        if x != 0:
            return "table-warning"
        else:
            return "table-info"


#! Journal Entry/ General Journal 
class JRE(AccModelBase):
    # helper functions
    def amount_validator(value:str):
        val = value.replace(",", "")
        if not val.isnumeric() or int(val) < 0:
            raise ValidationError(
                f"Invalid value: {value} should be a positive integer"
            ) 

    # class fields
    _img_path = 'images/JRE/'
    _img_def_path = 'images/default/JRE.png'
    _type = [
        ('d', 'DEBIT'),
        ('c', 'CREDIT'),
    ]

    # database fields
    date = models.DateField(default=timezone.now)
    number = models.PositiveIntegerField()
    batch = models.ForeignKey(JRB, verbose_name='batch', on_delete=models.CASCADE, limit_choices_to={'is_active':True}, related_name='journals', related_query_name='journal')
    ref = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    group = models.CharField(verbose_name="type",max_length=1, choices=_type)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    amount = models.PositiveIntegerField()
    account = models.ForeignKey(COA, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name='journals', related_query_name='journal')
    segment = models.ForeignKey(BSG, on_delete=models.RESTRICT, null=True, limit_choices_to={'is_active': True}, related_name='journals', related_query_name='journal')
    cashflow = models.ForeignKey(CCF, verbose_name="cash flow", null=True, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name='journals', related_query_name='journal')
    notes = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'created_jres', related_query_name='created_jrb')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=f'edited_jres', related_query_name='edited_jrb')

    class Meta:
        ordering = ('-date', '-number',)
        verbose_name = "JRE"
        verbose_name_plural = "JRE"

    # instance methods
    def __str__(self):
        batch = JRB.objects.get(number=self.batch)
        return f"{batch.number}-{self.ref}"

    def create_pair(self, **kwargs):
        p = type(self)()
        p.date = self.date 
        # p.number = self.number
        p.batch = self.batch
        p.ref = self.ref
        p.description = self.description
        p.group = self.group
        p.image = self.image
        p.amount = self.amount
        p.account = self.account
        p.segment = self.segment
        p.cashflow = self.cashflow
        p.notes = self.notes
        p.author = self.author
        p.edited_by = self.edited_by
        return p

    def save(self, *args, **kwargs):
        if not self.number:
            # auto input journal number
            last = type(self).objects.order_by('-created').first()
            now = timezone.now()
            if now.day == 1 and last.created.day > 1:
                n = now.date().strftime("%y%m%d") + "{:0>5}".format(0)
            else:
                n = int(str(last.number)[-5:]) + 1
                n = now.date().strftime("%y%m%d") + "{:0>5}".format(n)
            self.number = int(n)
            # auto input slug
            if not type(self).objects.filter(slug=self.number).exists():
                self.slug = slugify(str(self.number))
            else:
                s = str(self.number) + str(type(self).objects.count())
                self.slug = slugify(s)

        if settings.DEBUG:
            delete_model_image(self, type(self), type(self)._img_def_path)
            super(type(self), self).save(*args, **kwargs)
            resize_image(self.image.path)
        else:
            super(type(self), self).save(*args, **kwargs)

    def save_pair(self, pair:str):
        if "|" in pair:      # if account format is "NUMBER|ACCOUNT-NAME"
            numb, name = pair.split("|")
            qschecker = COA.actives.filter(Q(number=numb)&Q(name=name))
        else:
            qschecker = COA.actives.filter(name=pair)

        if qschecker.exists():
            pair_instance = self.create_pair()
            pair_instance.account = qschecker.first()
            pair_instance.group = type(self).get_group(debit_or_credit='credit', mode='short')
            self.group = type(self).get_group(mode='short')
            if not self.account.is_pnl: self.segment = None
            if not self.account.is_cashflow: self.cashflow = None
            if not pair_instance.account.is_pnl: pair_instance.segment = None
            if not pair_instance.account.is_cashflow: pair_instance.cashflow = None
            # save debit and credit journals
            self.save()
            pair_instance.save()
        else:
            raise ValidationError(f"No valid account found for {pair}")
        return (self.number, pair_instance.number)

    def get_tablerow_style(self):
        if self.group == 'c':
            return "table-info"
        else:
            return "table-light"

    @classmethod
    def get_group(cls, debit_or_credit:str="d", mode:str="long", opposite:bool=False):
        """
        TODO: get group constant
        debit_or_credit:
            if debit_or_credit == "d or debit" will return "debit" or "d" (alias)
            if debit_or_credit != "d or debit" will return "credit" or "c" (alias)
        mode:
            if mode == "long" (default) then will return 'debit' or 'credit' as defined in the class
            if mode != "long" then will return 'd' or 'c' as defined in the class (alias)
        """
        idx = 0
        if mode=="long": idx = 1
        if not opposite:
            if debit_or_credit.lower() == "debit" or debit_or_credit.lower() == "d":
                return cls._type[0][idx]
            else:
                return cls._type[1][idx]
        else:
            if debit_or_credit.lower() == "debit" or debit_or_credit.lower() == "d":
                return cls._type[1][idx]
            else:
                return cls._type[0][idx]
