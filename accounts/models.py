from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.conf import settings
from django.shortcuts import reverse
from company.models import Company
from media.api.manager import resize_image, delete_model_image


class Profile(models.Model):
    _img_path = 'images/profile/'
    _img_def_path = 'images/default/profile.png'
    _gender = [('female', 'Female'), ('male', 'Male')]
    _comp_level = [
        (0, 'Temporer'),
        (1, 'Staff'),
        (2, 'Supervisor'),
        (3, 'Manager'),
        (4, 'Senior Manager'),
        (5, 'Top Manager'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to=_img_path, default=_img_def_path)
    gender = models.CharField(max_length=6, choices=_gender, blank=True)
    address = models.CharField(max_length=125, blank=True)
    city = models.CharField(max_length=63, blank=True)
    phone = models.CharField(max_length=18, blank=True)
    job = models.CharField(max_length=63, blank=True)
    dob = models.DateTimeField(verbose_name='date of birth', blank=True, null=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    # company
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True, related_name="employees", related_query_name="employee")
    comp_stat = models.BooleanField("approved", default=False)
    comp_level = models.SmallIntegerField("level", choices=_comp_level, default=1)

    def __str__(self):
        return f'{self.user.username.capitalize()} profile'

    def get_absolute_url(self):
        return reverse("accounts:profile_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.username)

        if settings.DEBUG:
            delete_model_image(self, Profile, Profile._img_def_path) 
            super(Profile, self).save(*args, **kwargs)
            resize_image(self.image.path)
        else:
            super(Profile, self).save(*args, **kwargs)
