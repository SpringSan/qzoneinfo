# -*- coding: utf-8 -*-
# @Time    : 19-1-8 下午9:44
# @Author  : chunquansang
# @FileName: urls.py
# @Software: PyCharm

from django.conf.urls import url, include
from user import views
urlpatterns = [
    url(r'^login$', views.login),
    url(r'^login_ajax_check$', views.login_ajax_check),
    url(r'^signup$', views.signup),
    url(r'^index$', views.index),
    url(r'^logout$', views.logout),
    url(r'^base$', views.base),
    url(r'^forgotpassword$', views.forgotpassword),
    url(r'^signup_check$', views.signup_check),
    url(r'^username_check$', views.username_check),
    url(r'^headimg_upload$', views.headimg_upload)
]