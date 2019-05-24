# -*- coding: utf-8 -*-
# @Time    : 2019-03-11 09:54
# @Author  : chunquansang
# @FileName: urls.py
# @Software: PyCharm

from django.conf.urls import url, include
from qqinfo import views

urlpatterns = [
    url('^search_friend$', views.search_friend),
]