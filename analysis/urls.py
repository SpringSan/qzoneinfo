# -*- coding: utf-8 -*-
# @Time    : 2019-03-12 13:26
# @Author  : chunquansang
# @FileName: urls.py
# @Software: PyCharm

from django.conf.urls import url, include
from analysis import views

urlpatterns = [
    url('^emotionsdb_to_text$', views.emotions_db_to_text),
    url('^create_friend_emotion_fea$', views.create_friend_emotion_fea),
    url('^create_relationship_fea$', views.create_relationship_fea),
    url('^create_word_cloud$', views.create_word_cloud),
    url('^create_emotion_fea$', views.create_emotion_fea),
    url('^create_friend_tools_fea$', views.create_friend_tools_fea),
    url('^test$', views.create_relationship_fea),
    url('^create_deny_fea$', views.create_deny_fea),
    url('^create_popularest_emotion$', views.create_popularest_emotion),
]