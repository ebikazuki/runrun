# Generated by Django 2.2.2 on 2020-07-28 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0004_auto_20200728_1548'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Good',
        ),
        migrations.AddField(
            model_name='diary',
            name='good',
            field=models.IntegerField(blank=True, null=True, verbose_name='いいね'),
        ),
    ]
