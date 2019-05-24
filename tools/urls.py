# -*- coding: utf-8 -*-
# @Time    : 19-1-9 下午4:13
# @Author  : chunquansang
# @FileName: urls.py
# @Software: PyCharm



from django.conf.urls import url, include
from tools import views
urlpatterns = [
    url(r'^code$', views.verify_code)
]