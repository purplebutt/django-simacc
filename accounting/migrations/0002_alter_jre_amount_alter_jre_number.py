# Generated by Django 4.0.4 on 2022-08-31 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jre',
            name='amount',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='jre',
            name='number',
            field=models.PositiveBigIntegerField(),
        ),
    ]
