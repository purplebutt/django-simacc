# Generated by Django 4.1.2 on 2023-02-05 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0009_jre_pdf_alter_jre_account_alter_jre_cashflow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jre',
            name='pdf',
            field=models.FileField(default='documents/pdf/default/not_available.pdf', upload_to='documents/pdf/jre/'),
        ),
    ]