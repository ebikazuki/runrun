# Generated by Django 2.2.2 on 2020-08-09 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0010_good'),
    ]

    operations = [
        migrations.AddField(
            model_name='diary',
            name='twitter_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Twitterアカウント名'),
        ),
    ]
