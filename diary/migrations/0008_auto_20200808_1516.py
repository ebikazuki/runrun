# Generated by Django 2.2.2 on 2020-08-08 06:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0007_auto_20200729_1519'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diary',
            name='photo2',
        ),
        migrations.RemoveField(
            model_name='diary',
            name='photo3',
        ),
    ]
