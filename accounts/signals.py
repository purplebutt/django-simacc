from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def auto_create_post_on_user_save(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance).save()