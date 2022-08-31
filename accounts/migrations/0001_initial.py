# Generated by Django 4.0.4 on 2022-08-31 02:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='images/default/profile.png', upload_to='images/profile/')),
                ('gender', models.CharField(blank=True, choices=[('female', 'Female'), ('male', 'Male')], max_length=6)),
                ('address', models.CharField(blank=True, max_length=125)),
                ('city', models.CharField(blank=True, max_length=63)),
                ('phone', models.CharField(blank=True, max_length=18)),
                ('job', models.CharField(blank=True, max_length=63)),
                ('dob', models.DateTimeField(blank=True, null=True, verbose_name='date of birth')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='accounting.company')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
