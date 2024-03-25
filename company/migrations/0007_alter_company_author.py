# Generated by Django 4.1.2 on 2023-02-05 20:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0006_alter_company_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='author',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='comp_author', related_query_name='comp_author', to=settings.AUTH_USER_MODEL),
        ),
    ]