# -*- coding: utf-8 -*-
# @Time    : 2019-03-11 09:56
# @Author  : chunquansang
# @FileName: urls.py
# @Software: PyCharm

from django.conf.urls import url, include
from spider import views

urlpatterns = [
    url(r'^startspider$', views.start_spider),
    url(r'^make_cookie$', views.make_cookie),
]