from django.shortcuts import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from accounting.controllers.base import AccModelBase
from django.contrib.auth.models import User


class Company(AccModelBase):
    _img_path = 'images/company/'
    _img_def_path = 'images/default/company.png'
    _legal = [
        ('ud','UD'),
        ('cv','CV'),
        ('pt','PT'),
        ('lc','LLC'),
        ('kp','Koperasi'),
        ('ys','Yayasan'),
        ('ot','Lainnya'),
    ]
    name = models.CharField(max_length=255, unique=True)
    number = models.CharField(verbose_name="tax number", default="000.000.000", unique=True, max_length=30)
    legal = models.CharField(max_length=3, choices=_legal, default='ot')
    business_type = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=125)
    country = models.CharField(max_length=125)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=64, unique=True)
    desc = models.TextField(blank=True)
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    author = models.OneToOneField(User, on_delete=models.RESTRICT, related_name='comp_author', related_query_name='comp_author')
    edited_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='comp_editors', related_query_name='comp_editor')

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ('name',)

    def __str__(self):
        return self.name

    def sync_user_profile(self, commit=True, **kwargs):
        profile = self.author.profile
        profile.company = self
        profile.comp_stat = kwargs.get('stat')
        profile.comp_level = kwargs.get('level') or 1
        if commit: profile.save()
        return profile

    def get_absolute_url(self):
        return reverse("company:company_detail", kwargs={"slug": self.slug})
    

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.business_type = self.business_type.lower()
        self.city = self.city.lower()
        self.country = self.country.lower()
        if not self.pk:      # if company is newly created
            self.author = self.edited_by
            super(type(self), self).save(*args, **kwargs)
            self.sync_user_profile(stat=True, level=5)
            self.author.profile.save()  # make persistent on database
            # create config for the company
            config = Config()
            config.company = self
            config.save()
        else:
            super(type(self), self).save(*args, **kwargs)

    def get_legal_str(self):
        l = filter(lambda l: l[0]==self.legal, type(self)._legal)
        return tuple(l)[0][1]


class Config(AccModelBase):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='config', related_query_name='config')
    acc_period_current = models.DateField("accounting period", default=timezone.now)
    acc_period_closed = models.DateField("closed accounting period", default=timezone.now)

    def __str__(self):
        return f'{self.company.name} config'
