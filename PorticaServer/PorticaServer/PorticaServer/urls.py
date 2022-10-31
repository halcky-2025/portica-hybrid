"""
Definition of urls for Portima.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from app import views


urlpatterns = [
    path('', views.PostView.as_view(), name='home'),
    path('post', views.PostView.as_view()),
    path('task', views.TaskView.as_view()),
    path('order', views.OrderView.as_view()),
    path('output', views.OutputView.as_view()),
    path('ban', views.BanListView.as_view()),
    path('banexe', views.BanView.as_view()),
    path('admin/', admin.site.urls),
    path('input', views.InputView.as_view()),
    path('list', views.ListView.as_view()),
    path('auth', views.tweet)
]
