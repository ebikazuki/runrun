from accounts.models import CustomUser
from django.db import models


class Diary(models.Model):

    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.PROTECT)
    date = models.DateField(verbose_name='日付(例：2020-01-01)', blank=True, null=True)
    distance = models.FloatField(verbose_name='距離(km)', blank=True, null=True)
    twitter_name = models.CharField(verbose_name='Twitterアカウント名', max_length=50, blank=True, null=True)
    photo1 = models.ImageField(verbose_name='写真1', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)


    class Meta:
        verbose_name_plural = 'Diary'

    def __str__(self):
        return str(self.date)


class Good(models.Model):
    good = models.IntegerField(verbose_name='いいね', blank=True, null=True)
    class Meta:
        verbose_name_plural = 'Good'






