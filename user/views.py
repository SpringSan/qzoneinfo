from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from user.models import User
from tools.views import verify_code
import json
import os
from qzoneinfo.settings import BASE_DIR
import time
from PIL import ImageFile
import hashlib
from qzoneinfo.settings import MEDIA_ROOT
def login(request):
    verify_code(request)
    return render(request, 'user/login.html')


def login_ajax_check(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        vcode = request.POST.get('vcode').lower()
        vcode_session = request.session.get('vcode').lower()
        rememberme = request.POST.get('rememberme')
        print(rememberme)
        username =username.strip()
        try:
            user = User.objects.get(username=username)
            if vcode == vcode_session:
                if password == user.password:
                    isRemember = False
                    if rememberme == 'on':
                        isRemember = True
                    request.session['username'] = username
                    request.session['password'] = password
                    request.session['isLogin'] = True
                    request.session['pic'] = str(user.image)
                    message = 'ok'
                    return JsonResponse({'message': message})
                else:
                    message = 'pass_failed'
                    return JsonResponse({'message': message})
            else:
                message = 'code_failed'
                return JsonResponse({'message': message})
        except:
            message = 'user_failed'
        return JsonResponse({'message': message})
    return render(request, 'user/login.html')

def success(request):
    if request.session.get('isLogin'):
        return redirect('user/index.html')

def signup(request):
    return render(request, 'user/signup.html')


def signup_check(request):
    message = 'signupok'
    json_path = os.path.join(BASE_DIR, 'static/json/sql_json_childfa.json')
    with open(json_path, encoding='utf-8') as f:
        areas = json.load(f)
    if request.method == 'POST':
        username = request.POST.get('username')
        print(username)
        password = request.POST.get('password')
        print(password)
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        birth = request.POST.get('birth')
        image = request.FILES.get('fileup')
        pic_path = os.path.join(MEDIA_ROOT, 'user')
        print(request.FILES)
        print(image)
        if address:
            for area in areas:
                if area == address:
                    city = areas[area]['parent'][0]['cname']
                    province = areas[area]['parent'][1]['cname']
                    dis = areas[area]['cname']
                    address = '' + province + city + dis
                    break
        if birth:
            birth = birth.split()
            months_zh= ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
            for i, value in enumerate(months_zh):
                if birth[1] == months_zh[i]:
                    birth[1] = '0'+str(i+1) if i<9 else str(i+1)
                    break
            birth = birth[2]+'-'+birth[1]+'-'+birth[0]
        if image:
            image = headimg_upload(image, pic_path)
        try:
            new_user = User.objects.create(username=username, password=password, birth=birth, gender=gender, address=address, email=email, image=image)
            new_user.save()

        except:
            message = 'insert error'
    return render(request, 'user/login.html', {'message': message})

def index(request):
    pass
    return render(request, 'user/index.html')

def logout(request):
    pass
    return render(request, 'user/index.html')
def base(request):
    pass
    return render(request, 'user/base.html')

def forgotpassword(request):
    pass
    return render(request, 'user/forgotpassword.html')

def username_check(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        username = username.strip()
        try:
            User.objects.get(username=username)
            jsonResult = {"valid": False}
        except:
            jsonResult = {"valid": True}
    return JsonResponse(jsonResult)

def headimg_upload(file, path):
    if file:
        _n = "%d" % (time.time()*1000)
        _f = time.strftime('%Y%m%d', time.localtime())
        file_name = _f + _n + '.png'
        path_file = os.path.join(path, file_name)
        parse = ImageFile.Parser()
        for chunk in file.chunks():
            parse.feed(chunk)
        img = parse.close()
        try:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(path_file, 'jpeg', quality=100)
        except:
            return None
        return file_name
    return None

def hash_code(s, salt='qzoneinfo'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()
