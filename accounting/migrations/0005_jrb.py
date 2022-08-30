# Generated by Django 4.0.4 on 2022-08-24 19:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0004_bsg'),
    ]

    operations = [
        migrations.CreateModel(
            name='JRB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=30, unique=True)),
                ('description', models.CharField(max_length=125)),
                ('slug', models.SlugField(blank=True, max_length=125, unique=True)),
                ('group', models.CharField(max_length=125, verbose_name='type')),
                ('image', models.ImageField(default='images/default/JRB.png', upload_to='images/JRB/')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'JRB',
                'verbose_name_plural': 'JRB',
                'ordering': ('number',),
            },
        ),
    ]
