from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.shortcuts import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from .base import AccModelBase
from .jrb import JRB; from .coa import COA; from .bsg import BSG; from .ccf import CCF
from django.contrib.auth.models import User


class JRE(AccModelBase):
    # helper functions
    def amount_validator(value:str):
        val = str(value).replace(",", "")
        if not val.isnumeric() or int(val) < 0:
            raise ValidationError(
                f"Invalid value: {value} should be a positive integer"
            ) 
        elif int(val) > 99_999_999_999_999:
            raise ValidationError(
                f"Max value: 99,999,999,999,999"
            ) 

    def date_validator(value):
        today = timezone.now().date()
        if value > today:
            raise ValidationError(
                f"Invalid value: {value} should be a date <= today"
            )

    # class fields
    _img_path = 'images/jre/'
    _img_def_path = 'images/default/jre.png'
    _type = [
        ('d', 'DEBIT'),
        ('c', 'CREDIT'),
    ]

    # database fields
    date = models.DateField(default=timezone.now, validators=[date_validator])
    number = models.PositiveBigIntegerField()
    batch = models.ForeignKey(JRB, verbose_name='batch', on_delete=models.CASCADE, limit_choices_to={'is_active':True}, related_name='journals', related_query_name='journal')
    ref = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    group = models.CharField(verbose_name="type",max_length=1, choices=_type)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    amount = models.PositiveBigIntegerField(validators=[amount_validator])
    account = models.ForeignKey(COA, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name='journals', related_query_name='journal')
    segment = models.ForeignKey(BSG, on_delete=models.RESTRICT, null=True, limit_choices_to={'is_active': True}, related_name='journals', related_query_name='journal')
    cashflow = models.ForeignKey(CCF, verbose_name="cash flow", null=True, on_delete=models.CASCADE, 
        limit_choices_to={'is_active': True}, related_name='journals', related_query_name='journal')
    notes = models.TextField(blank=True)
    pair = models.OneToOneField('JRE', default=None, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='jre_authors', related_query_name='jre_author')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='jre_editors', related_query_name='jre_editor')

    class Meta:
        ordering = ('-date', '-number', '-group')
        verbose_name = "JRE"
        verbose_name_plural = "JRE"

    # instance methods
    def __str__(self):
        batch = JRB.objects.get(number=self.batch)
        return str(self.number)

    def set_opp_group(self, pair)->None:
        """
        TODO: Set opposite group
        pair = pair account to be evaluate.
        If pair.group = 'd' (debit) then set self.group to 'c' (credit) and vice versa
        """
        self.group = type(self).get_group(pair.group, mode='short', opposite=True)

    def make_pair(self, target=None, mode='create'):
        if target is None: target = type(self)()
        # p.number = self.number

        target.date = self.date 
        target.batch = self.batch
        target.ref = self.ref
        target.description = self.description
        target.image = self.image
        target.amount = self.amount
        target.notes = self.notes
        target.edited_by = self.edited_by
        if mode == 'create':
            target.group = self.group
            target.account = self.account
            target.segment = self.segment
            target.cashflow = self.cashflow
            target.author = self.author
        return target

    def save(self, *args, **kwargs):
        if not self.number:
            # auto input journal number
            last = type(self).objects.order_by('-created').first()
            now = timezone.now()
            if (last == None) or (now.day == 1 and last.created.day > 1):
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
        # remove segment if account not Profit and Loss
        # remove cashflow if account not CashFlow
        if not self.account.is_pnl: self.segment = None
        if not self.account.is_cashflow: self.cashflow = None
        super(type(self), self).save(*args, **kwargs)

    def save_pair(self, pair:str):
        if "|" in pair:      # if account format is "NUMBER|ACCOUNT-NAME"
            numb, name = pair.split("|")
            qschecker = COA.actives.filter(Q(number=numb)&Q(name=name))
        else:
            qschecker = COA.actives.filter(name=pair)

        if qschecker.exists():
            pair_instance = self.make_pair()
            pair_instance.account = qschecker.first()
            pair_instance.group = type(self).get_group(debit_or_credit='credit', mode='short')
            self.group = type(self).get_group(mode='short')
            # add pair and save debit and credit journals
            pair_instance.save()        # save pair so it can be add to self
            self.pair = pair_instance   # add pair (already save on database) to self
            self.save()                 # self can be save now because pair already exists
            pair_instance.pair = self   # set pair for pair_instance with value of self
            pair_instance.save()        # re-save pair_instance
        else:
            raise ValidationError(f"No valid account found for {pair}")
        return (self.number, pair_instance.number)

    def update_pair(self):
        if self.pair:
            pair_instance = self.make_pair(self.pair, mode='update')
            # add pair and save debit and credit journals
            pair_instance.pair = self           # add pair to pair_instance, this will ensure pair between journal
            pair_instance.set_opp_group(self)   # set pair to debit if self.group is credit and vice versa
            pair_instance.save()
            self.save()
        else:
            raise ValidationError(f"No valid account found for {pair}")
        return (self.number, pair_instance.number)

    def get_delete_url(self):
        return reverse(f"accounting:{type(self).__name__.lower()}_delete", kwargs={'slug':self.slug})

    def get_tablerow_style(self):
        if self.group == 'd': return "table-info"
        else: return "table-light"

    @classmethod
    def get_add_single_url(cls):
        return reverse(f'{cls.app_name}:{cls.__name__.lower()}_add_single')

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
