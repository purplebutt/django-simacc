# Generated by Django 4.0.4 on 2022-09-01 19:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, max_length=125, unique=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('number', models.CharField(default='000.000.000', max_length=30, unique=True, verbose_name='tax number')),
                ('legal', models.CharField(choices=[('ud', 'UD'), ('cv', 'CV'), ('pt', 'PT'), ('lc', 'LLC'), ('kp', 'Koperasi'), ('ys', 'Yayasan'), ('ot', 'Lainnya')], default='ot', max_length=3)),
                ('business_type', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=125)),
                ('country', models.CharField(max_length=125)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('email', models.EmailField(max_length=64, unique=True)),
                ('desc', models.TextField(blank=True)),
                ('image', models.ImageField(default='images/default/company.png', upload_to='images/company/')),
                ('author', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, related_name='comp_authors', related_query_name='comp_author', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='comp_editors', related_query_name='comp_editor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, max_length=125, unique=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('acc_period_current', models.DateField(default=django.utils.timezone.now, verbose_name='accounting period')),
                ('acc_period_closed', models.DateField(default=django.utils.timezone.now, verbose_name='closed accounting period')),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='config', related_query_name='config', to='company.company')),
            ],
            options={
                'ordering': ('-created',),
                'abstract': False,
            },
        ),
    ]
