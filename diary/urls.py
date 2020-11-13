from django.urls import path

from . import views


app_name = 'diary'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    path('diary-list/', views.DiaryListView.as_view(), name="diary_list"),
    path('diary-detail/<int:pk>/', views.DiaryDetailView.as_view(), name="diary_detail"),
    path('diary-create/', views.DiaryCreateView.as_view(), name="diary_create"),
    path('diary-update/<int:pk>/', views.DiaryUpdateView.as_view(), name="diary_update"),
    path('diary-delete/<int:pk>/', views.DiaryDeleteView.as_view(), name="diary_delete"),
    path('good/', views.good, name='good'),
    path('diary_list/plot/<int:pk>/', views.get_svg, name='plot'),
    path('diary_list/twitter/<int:pk>/', views.twitter, name='twitter'),
    path('twitter_connect/', views.TwitterConnectView.as_view(), name="twitter_connect"),
    path('twitter_change/<int:pk>/', views.TwitterChangeView.as_view(), name="twitter_change"),
]
