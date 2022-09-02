# Generated by Django 4.0.4 on 2022-09-01 01:09

import accounting.controllers.jre
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_alter_jre_amount_alter_jre_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jre',
            options={'ordering': ('-date', '-group'), 'verbose_name': 'JRE', 'verbose_name_plural': 'JRE'},
        ),
        migrations.AddField(
            model_name='jre',
            name='pair',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='accounting.jre'),
        ),
        migrations.AlterField(
            model_name='jre',
            name='amount',
            field=models.PositiveBigIntegerField(validators=[accounting.controllers.jre.JRE.amount_validator]),
        ),
    ]