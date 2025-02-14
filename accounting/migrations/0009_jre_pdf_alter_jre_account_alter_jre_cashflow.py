# Generated by Django 4.0.4 on 2022-09-14 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0008_alter_jre_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='jre',
            name='pdf',
            field=models.FileField(default='images/default/jre.png', upload_to='images/jre/'),
        ),
        migrations.AlterField(
            model_name='jre',
            name='account',
            field=models.ForeignKey(limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.RESTRICT, related_name='journals', related_query_name='journal', to='accounting.coa'),
        ),
        migrations.AlterField(
            model_name='jre',
            name='cashflow',
            field=models.ForeignKey(limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='journals', related_query_name='journal', to='accounting.ccf', verbose_name='cash flow'),
        ),
    ]
