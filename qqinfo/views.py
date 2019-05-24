from django.shortcuts import render, redirect

# Create your views here.
from django.shortcuts import render
from qqinfo.models import QQInfo
from qzoneinfo.settings import BASE_DIR
from django.http.response import HttpResponse, JsonResponse
from tools.views import page_to_page
import json

def search_friend(request):
    if request.method == 'GET':
        master = request.session.get('qq')
        search = request.GET.get('search')
        data=''
        friend_list=''
        try:
            friends = QQInfo.objects.filter(nick__contains=search)
        except Exception as e:
            print(e)
        else:
            if friends:
                data, friend_list = page_to_page(request, 10, friends)
        return render(request, 'user/index.html', {
            'friend_list': friend_list,
            'qq': master,
            'data': data,
            'search': search,
        })