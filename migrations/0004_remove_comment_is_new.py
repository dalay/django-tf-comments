# Generated by Django 2.1.2 on 2018-10-03 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_auto_20180718_1529'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='is_new',
        ),
    ]
