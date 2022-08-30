# Generated by Django 4.0.4 on 2022-08-27 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0011_alter_jre_cashflow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jre',
            name='cashflow',
            field=models.ForeignKey(limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='journals', related_query_name='journal', to='accounting.ccf', verbose_name='cash flow'),
        ),
    ]
