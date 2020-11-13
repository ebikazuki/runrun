import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import redirect
from .forms import InquiryForm, DiaryCreateForm, TwitterForm
from .models import Diary
from .models import Good
from django.db.models import Sum
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import os
from django.http import HttpResponse
import datetime
import matplotlib.dates as mdates
import twitter

#twitter-pythonのAPI認証
t = twitter.Api(consumer_key = os.environ.get('CONSUMER_KEY'),
                  consumer_secret = os.environ.get('CONSUMER_SECRET'),
                  access_token_key = os.environ.get('ACCESS_TOKEN_KEY'),
                  access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')
                  )

logger = logging.getLogger(__name__)


class IndexView(generic.TemplateView):
    template_name = "index.html"

class InquiryView(generic.FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('diary:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました。')
        logger.info('Inquiry sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)

class DiaryListView(LoginRequiredMixin, generic.ListView):
    model = Diary
    template_name = 'diary_list.html'
    paginate_by = 7

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sum = Diary.objects.filter(user=self.request.user).aggregate(Sum('distance'))
        context['Sum'] = sum['distance__sum']
        frag = Diary.objects.filter(user=self.request.user).first()
        if sum['distance__sum'] != None:
            point = float(sum['distance__sum']//50)
            delta = 50-sum['distance__sum']%50
            #ユーザー名picのIDを入れている。開発環境:6,本番:10
            img_ob = Diary.objects.filter(user = 10,distance = point).first()
            context['Img_url'] = img_ob.photo1.url
            context['Delta'] = delta
        if frag != None:
            diary_ob = Diary.objects.filter(user=self.request.user).order_by('-date').first()
            context['User_pk'] = diary_ob.pk
        return context

    def get_queryset(self):
        diaries = Diary.objects.filter(user=self.request.user).order_by('-date')
        return diaries

class DiaryDetailView(LoginRequiredMixin, generic.DetailView):
    model = Diary
    template_name = 'diary_detail.html'

class DiaryCreateView(LoginRequiredMixin, generic.CreateView):
    model = Diary
    template_name = 'diary_create.html'
    form_class = DiaryCreateForm
    success_url = reverse_lazy('diary:diary_list')

    def form_valid(self, form):
        diary = form.save(commit=False)
        diary.user = self.request.user
        diary.save()
        messages.success(self.request, '記録を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "記録の作成に失敗しました。")
        return super().form_invalid(form)

class DiaryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Diary
    template_name = 'diary_update.html'
    form_class = DiaryCreateForm

    def get_success_url(self):
        return reverse_lazy('diary:diary_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, '記録を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "記録の更新に失敗しました。")
        return super().form_invalid(form)

class DiaryDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Diary
    template_name = 'diary_delete.html'
    success_url = reverse_lazy('diary:diary_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "記録を削除しました。")
        return super().delete(request, *args, **kwargs)


#Goodボタンの動作
def good(request):

    post = Good.objects.get(id=1)
    if request.method == 'POST':
        # データの新規追加
        if isinstance(post.good,int):
            post.good += 1
        else:
            post.good = 1

        post.save()

    return redirect('diary:diary_list')

#グラフの描画
def setPlt(pk):
    count = 0
    x=[]
    y=[]
    diaries = Diary.objects.get(id=pk)
    user = diaries.user
    diary_ob = Diary.objects.filter(user=user).order_by('-date')
    for ob in diary_ob:
        if ob.date != None:
            count += 1
            x.append(ob.date)
            y.append(ob.distance)
            if count == 7:
                break
    plt.bar(x, y, color='#00d5ff')
    plt.title(r"$\bf{One Week Trend}$", color='#3407ba')
    plt.xlabel('date')
    plt.ylabel("km")
    plt.xlim(x[0]-datetime.timedelta(days=6.5), x[0]+datetime.timedelta(days=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

# svgへの変換
def pltToSvg():
    buf = io.BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight')
    s = buf.getvalue()
    buf.close()
    return s

#グラフ描画のメイン動作
def get_svg(request,pk):
    setPlt(pk)
    svg = pltToSvg()
    plt.cla()
    response = HttpResponse(svg, content_type='image/svg+xml')
    return response

# Tweetから「km」の前の数値を取得する関数
def run_dist(string):
    result = 0
    count = string.count("km")
    while count > 0:
        k = string.find("km")
        for i in range(1, 10):
            frag = str.isdecimal(string[k - i])
            if not frag:
                break
        result += int(string[k + 1 - i:k])
        count -= 1
        string = string[k + 1:]

    return result

# twitterの時間を変換する関数
def date_conv(str):
    # strはSun Aug 02 13:13:05 +0000 2020という形式
    year, month, date = str[26:30], str[4:7], str[8:10]
    tdatetime = datetime.datetime.strptime(year + month + date, '%Y%b%d')
    # 日本時間へ変換
    tdatetime_jp = tdatetime + datetime.timedelta(hours=9)
    tdate_jp = datetime.date(tdatetime_jp.year, tdatetime_jp.month, tdatetime_jp.day)

    return tdate_jp

# 過去一週間のランニングデータをTwitterから集める関数
def data_gather(name):
    end = datetime.date.today() + datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=8)
    tweet = t.GetSearch(term='#runrun from:' + name + ' since:' + str(start) + ' until:' + str(end) + '_JST')
    date_list = []
    distance_list = []

    for s in tweet:
        date = date_conv(s.created_at)
        date_list.append(date)
        distance = run_dist(s.text)
        distance_list.append(distance)

    return date_list, distance_list

#Twitterボタンの動作
def twitter(request,pk):

    diaries = Diary.objects.get(id=pk)
    user = diaries.user
    twitter_name_ob = Diary.objects.filter(user=user).order_by("twitter_name").first()
    twitter_id = twitter_name_ob.twitter_name
    if twitter_id != None:
        date_list,distance_list = data_gather(twitter_id)
        y = 0
        for x in date_list:
            if Diary.objects.filter(user=user,date=x).first()==None:
                record = Diary(user=user, date=x, distance=distance_list[y])
                record.save()
            else:
                '''
                record_id = Diary.objects.filter(user=user, date=x).first().id
                record = Diary.objects.get(id=record_id)
                record.distance += distance_list[y]
                record.save()
                '''
            y += 1
    return redirect('diary:diary_list')

class TwitterConnectView(LoginRequiredMixin, generic.CreateView):
    model = Diary
    template_name = 'twitter_connect.html'
    form_class = TwitterForm
    success_url = reverse_lazy('diary:diary_list')

    def form_valid(self, form):
        diary = form.save(commit=False)
        diary.user = self.request.user
        diary.save()
        messages.success(self.request, 'Twitter名を登録しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Twitter名の登録に失敗しました。")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        twitter_name_ob = Diary.objects.filter(user=self.request.user).order_by("twitter_name").first()
        if twitter_name_ob != None:
            twitter_id = twitter_name_ob.twitter_name
            context['Twitter_name'] = twitter_id
            context['pk'] = twitter_name_ob.pk
        else:
            context['Twitter_name'] = None
        return context

class TwitterChangeView(LoginRequiredMixin, generic.UpdateView):
    model = Diary
    template_name = 'twitter_change.html'
    form_class = TwitterForm
    success_url = reverse_lazy('diary:diary_list')

    '''
    def get_success_url(self):
        return reverse_lazy('diary:diary_detail', kwargs={'pk': self.kwargs['pk']})
    '''


    def form_valid(self, form):
        messages.success(self.request, 'Twitter名を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Twitter名を更新に失敗しました。")
        return super().form_invalid(form)
