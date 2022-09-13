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
    _valid_config_keys = ('closed_period', 'current_period')

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
    config = models.JSONField(default=dict)
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
        self.business_type = self.business_type.title()
        self.city = self.city.title()
        self.country = self.country.title()
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

    def get_employees(self):
        employees = User.objects.filter(profile__company=self)
        return employees

    def get_pending_employees(self):
        employees = User.objects.filter(profile__company=self, profile__comp_stat=False)
        return employees

    def save_config(self, config:dict):
        if isinstance(config, dict):
            self.config = config
        else:
            self.config = dict()
        super(type(self), self).save()


    def get_time_zone(self):
        tz = self.config.get('time_zone')
        if isinstance(tz, list): tz=tz.pop()
        return tz

    def get_closed_period(self):
        dt = self.config.get('closed_period')
        if isinstance(dt, list): dt=dt.pop()
        dt = timezone.datetime.fromisoformat(dt)
        return dt
        
    def get_current_period_start(self):
        dt = self.config.get('current_period_start')
        if isinstance(dt, list): dt=dt.pop()
        dt = timezone.datetime.fromisoformat(dt)
        return dt

    def get_current_period_end(self):
        dt = self.config.get('current_period_end')
        if isinstance(dt, list): dt=dt.pop()
        dt = timezone.datetime.fromisoformat(dt)
        return dt
