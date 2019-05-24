from django.shortcuts import render

# Create your views here.
from qqinfo.models import QQInfo, CommentInfo, LikeInfo, EmotionInfo
from selenium import webdriver
from time import sleep
import re
import json
import os
from qzoneinfo.settings import BASE_DIR
import requests
import urllib
from django.utils import timezone as datetime
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

def make_cookie(request):
    message=''
    if request.method == 'POST':
        qq = request.POST.get('qq')
        qqpassword = request.POST.get('qqpassword')
        qq = qq.strip()
        request.session['qq'] = qq
        request.session['qqpassword'] = qqpassword
        driver = webdriver.Chrome('/Users/sangchunquan/software/chromedriver')
        driver.get('https://user.qzone.qq.com/{}/main'.format(qq))
        driver.switch_to_frame('login_frame')
        driver.find_element_by_id('switcher_plogin').click()
        driver.find_element_by_id('u').send_keys(qq)
        driver.find_element_by_id('p').send_keys(qqpassword)
        driver.find_element_by_id('login_button').click()
        sleep(1)
        html = driver.page_source
        cookies = driver.get_cookies()
        try:
            g_qzonetoken=re.search('window\.g_qzonetoken = \(function\(\)\{ try\{return (.*?);\} catch\(e\)',html)
            g_qzonetoken = str(g_qzonetoken[0]).split('\"')[1]
        except Exception as e:
            message='passworderr'
        else:
            message='passwordsucc'
            cookie_dic={}
            cookie_dic['g_qzonetoken'] = g_qzonetoken
            for cookie in cookies:
                if 'name' in cookie and 'value' in cookie:
                    cookie_dic[cookie['name']] = cookie['value']
                with open(os.path.join(BASE_DIR, 'static/conf/cookie_dic.txt'), 'w') as f:
                    json.dump(cookie_dic, f)
    try:
        friends = QQInfo.objects.filter()
    except Exception as e:
        message = '读取好友失败'
    else:
        p = Paginator(friends, 11)  # 分页，3篇文章一页
        if p.num_pages <= 1:  # 如果文章不足一页
            friend_list = friends  # 直接返回所有文章
            data = ''  # 不需要分页按钮
        else:
            page = int(request.GET.get('page', 1))  # 获取请求的文章页码，默认为第一页
            friend_list = p.page(page)  # 返回指定页码的页面
            left = []  # 当前页左边连续的页码号，初始值为空
            right = []  # 当前页右边连续的页码号，初始值为空
            left_has_more = False  # 标示第 1 页页码后是否需要显示省略号
            right_has_more = False  # 标示最后一页页码前是否需要显示省略号
            first = False  # 标示是否需要显示第 1 页的页码号。
            # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
            # 其它情况下第一页的页码是始终需要显示的。
            # 初始值为 False
            last = False  # 标示是否需要显示最后一页的页码号。
            total_pages = p.num_pages
            page_range = p.page_range
            if page == 1:  # 如果请求第1页
                right = page_range[page:page + 2]  # 获取右边连续号码页
                print(total_pages)
                if right[-1] < total_pages - 1:  # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
                    # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
                    right_has_more = True
                if right[-1] < total_pages:  # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
                    # 所以需要显示最后一页的页码号，通过 last 来指示
                    last = True
            elif page == total_pages:  # 如果请求最后一页
                left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
                if left[0] > 2:
                    left_has_more = True  # 如果最左边的号码比2还要大，说明其与第一页之间还有其他页码，因此需要显示省略号，通过 left_has_more 来指示
                if left[0] > 1:  # 如果最左边的页码比1要大，则要显示第一页，否则第一页已经被包含在其中
                    first = True
            else:  # 如果请求的页码既不是第一页也不是最后一页
                left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
                right = page_range[page:page + 2]  # 获取右边连续号码页
                if left[0] > 2:
                    left_has_more = True
                if left[0] > 1:
                    first = True
                if right[-1] < total_pages - 1:
                    right_has_more = True
                if right[-1] < total_pages:
                    last = True
            data = {  # 将数据包含在data字典中
                'left': left,
                'right': right,
                'left_has_more': left_has_more,
                'right_has_more': right_has_more,
                'first': first,
                'last': last,
                'total_pages': total_pages,
                'page': page
            }
        qq = request.session.get('qq')
        return render(request, 'user/index.html', context={
            'friend_list': friend_list,
            'data': data,
            'qq': qq,
            'message': message
        })
#爬虫类
class Qzone:
    def __init__(self, cookie, header):
        self.denyfriend = []
        self.cookie = cookie
        self.header = header
        self.qq_list = []

    def get_gtk(self):
        p_skey = self.cookie['p_skey']
        hash = 5381
        for letter in p_skey:
            hash += (hash << 5) + ord(letter)
            g_tk = hash & 2147483647
        return g_tk

#    def get_qzonetoken(self):

    def get_uin(self):
        uin = self.cookie['ptui_loginuin']
        return uin

 #   def get_qqfriend(self):

    def get_qq(self):
        with open('friend.txt', 'r') as f:
            friend_list = json.load(f)
        for friend in friend_list:
            self.qq_list.append(friend['data'])
        return self.qq_list

    def get_friendlist(self, request):
        url_friend = 'https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?'
        g_tk = self.get_gtk()
        uin = self.get_uin()
        params = {
            'uin': uin,
            'action': 1,
            'fupdate': 1,
            'g_tk': g_tk,
            'g_qzonetoken': self.cookie['g_qzonetoken']
        }
        url_friend += urllib.parse.urlencode(params)
        t = True
        offset = 0
        friend_list = []
        while(t):
            url_friend_ = url_friend + '&offset=' + str(offset)
            result = requests.get(url_friend_, headers=self.header, cookies=self.cookie)
            friend_json = re.findall('\((.*)\)', result.text, re.S)[0]
            friend_list.extend(json.loads(friend_json)['data']['uinlist'])
            if len(json.loads(friend_json)['data']['uinlist'])==0 :
                t = False
            offset += 50
        for i in range(0,len(friend_list)):
            imgurl = 'http://qlogo.store.qq.com/qzone/' + \
                           friend_list[i]['data'] + '/' + friend_list[i]['data'] + '/100'
            try:
                qqinfo = QQInfo.objects.get(qq=friend_list[i]['data'])
            except:
                qqinfo = None
            try:
                if qqinfo is None:
                    new_qqinfo = QQInfo.objects.create(qq=friend_list[i]['data'], nick=friend_list[i]['label'], qqimg=imgurl)
                    new_qqinfo.save()
            except:

                message="new qq insert error"
        master_imgurl = 'http://qlogo.store.qq.com/qzone/' + \
                  request.session.get('qq') + '/' + request.session.get('qq') + '/100'
        try:
            qqinfo = QQInfo.objects.get(qq=request.session.get('qq'))
        except:
            qqinfo = None
        try:
            if qqinfo is None:
                master_qqinfo = QQInfo.objects.create(qq=request.session.get('qq'), nick="您",
                                                   qqimg=master_imgurl)
                master_qqinfo.save()
        except:
            message = "new qq insert error"
        print('你共有' + str(len(friend_list)) + "位好友")

    def get_like(self, emotion_id, msglist, qq, name):
        likeinfo = {}
        g_tk = self.get_gtk()
        uin = self.get_uin()
        qzonetoken = self.cookie['g_qzonetoken']
        url_like = 'https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?'
        if msglist['content'] is None:
            return 0
        tid = msglist['tid']
        if 'rt_uin' in msglist.keys() and 'rt_tid' in msglist.keys():
            return 0
        params_like = {
            'uin': uin,
            'unikey': 'http://user.qzone.qq.com/' + str(qq) + '/mood/' + str(tid) + '.1',
            'begin_uin': 0,
            'query_count': 60,
            'if_first_page': 1,
            'g_tk': g_tk,
            'qzonetoken': qzonetoken
        }
        params_like_encode = urllib.parse.urlencode(params_like)
        url_like += params_like_encode
        result = requests.get(url_like, headers = self.header, cookies = self.cookie)
        result.encoding = 'UTF-8'
        r = re.findall('\((.*)\)', result.text, re.S)[0]
        r = json.loads(r)
        if 'data' not in r.keys():
            return 0
        if 'like_uin_info' not in r['data'].keys():
            return 0
        for like in r['data']['like_uin_info']:
            try:
                from_qq = QQInfo.objects.get(qq=like['fuin'])
            except Exception as get_fromqqerr:
                from_qq = None
            try:
                to_qq = QQInfo.objects.get(qq=qq)
            except Exception as get_toqqerr:
                to_qq = None
            try:
                emotion = EmotionInfo.objects.get(id=emotion_id)
            except Exception as get_emotionerr:
                emotion = None

            if from_qq and to_qq and emotion:
                try:
                    likeinfo = LikeInfo.objects.create(from_qq=from_qq, to_qq=to_qq,emotion=emotion)
                    likeinfo.save()
                except Exception as ins_likeerr:
                    message="insert like error"

    def get_comment(self, emotion_id, msglist, qq, name):
        commentinfo = {}
        g_tk = self.get_gtk()
        uin = self.get_uin()
        qzonetoken = self.cookie['g_qzonetoken']
        if 'content' not in msglist.keys():
            return 0
        if msglist['content'] is None:
            return 0
        if 'commentlist' in msglist.keys():
            if msglist['commentlist'] is None:
                return 0
            for comment in msglist['commentlist']:
                try:
                    from_qq = QQInfo.objects.get(qq=comment['uin'])
                except Exception as get_fromqqerr:
                    from_qq = None
                try:
                    to_qq = QQInfo.objects.get(qq=qq)
                except Exception as get_toqqerr:
                    to_qq = None
                try:
                    emotion = EmotionInfo.objects.get(id=emotion_id)
                except Exception as get_emotionerr:
                    emotion = None
                if from_qq and to_qq and emotion:
                    create_time = datetime.datetime.fromtimestamp(int(comment['create_time']))
                    try:
                        commentinfo = CommentInfo.objects.create(content=comment['content'],
                                                                 create_time=create_time,
                                                                 from_qq=from_qq,
                                                                 to_qq=to_qq,
                                                                 emotion=emotion)
                        commentinfo.save()
                    except Exception as ins_commenterr:
                        message="insert comment error"
            if msglist['cmtnum'] > 20:
                params_more20 = {
                    'uin': qq,
                    'topicId': str(qq) + '_' + msglist['tid'],
                    'ftype': 0,
                    'sort': 0,
                    'order': 20,
                    'start': 20,
                    'num': 20,
                    't1_source': 'undefined',
                    'callback': '_preloadCallback',
                    'code_version': 1,
                    'format': 'jsonp',
                    'need_private_comment': 1,
                    'g_tk': g_tk,
                    'qzonetoken': qzonetoken
                }
                url_more20 = 'https://h5.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_getcmtreply_v6?'
                url_more20 += urllib.parse.urlencode(params_more20)
                res_more20 = requests.get(url_more20, headers=self.header, cookies=self.cookie)
                r_more20 = re.findall('\((.*)\)', res_more20.text, re.S)[0]
                comment_more20 = json.loads(r_more20)
                data = comment_more20['data']
                if 'comments' not in data.keys():
                    return 0
                for comment in data['comments']:
                    try:
                        from_qq = QQInfo.objects.get(qq=comment['poster']['id'])
                    except Exception as get_fromqqerr:
                        from_qq = None
                    try:
                        to_qq = QQInfo.objects.get(qq=qq)
                    except Exception as get_toqqerr:
                        to_qq = None
                    try:
                        emotion = EmotionInfo.objects.get(id=emotion_id)
                    except Exception as get_emotionerr:
                        emotion = None
                    if from_qq and to_qq and emotion:
                        create_time = datetime.datetime.fromtimestamp(int(comment['postTime']))
                        try:
                            commentinfo = CommentInfo.objects.create(content=comment['content'],
                                                                     create_time=create_time,
                                                                     from_qq=from_qq,
                                                                     to_qq=to_qq,
                                                                     emotion=emotion)
                            commentinfo.save()
                        except Exception as ins_commenterr:
                            message = "insert comment error"

    def get_emotion(self, qq, name):
        page = 1
        # conti循环的标志，当为false时退出循环
        conti = True
        pos = 0
        g_tk = self.get_gtk()
        uin = self.get_uin()
        while conti:
            # url必须在循环内，每次循环必须重置
            url = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
            params = {
                'uin': qq,
                'pos': pos,
                'num': 20,
                'hostUin': uin,
                'replynum': 100,
                'callback': '_preloadCallback',
                'code_version': 1,
                'format': 'jsonp',
                'need_private_comment': 1,
                'g_tk': g_tk,
                'qzonetoken': self.cookie['g_qzonetoken']
            }
            pos += 20
            url += urllib.parse.urlencode(params)
            res = requests.get(url, headers=self.header, cookies=self.cookie)
            print('读取 ' + name + ' 的第 ' + str(page) + ' 页说说成功')
            page += 1
            # 匹配出_preloadCallback之后的内容
            r = re.findall('\((.*)\)', res.text)[0]
            # 将json数据变成字典格式
            msg = json.loads(r)
            if msg['code'] == -10031:
                print("好友：" + name + ":" +str(qq) + " 屏蔽您的访问")
                denyfriend_dic = {}
                denyfriend_dic['name'] = name
                denyfriend_dic['qq'] = qq
                self.denyfriend.append(denyfriend_dic)
                return 0
            if 'msglist' not in msg:
                return 0
            # 这里爬说说结束，注意和上面的区别，一个是不存在键值，一个是存在键，但值类型为None

            if msg['msglist'] == None:
                print('\n' + name + '的空间无更多说说' + '\n')
                return 0

            msglist = msg['msglist']

            if msglist is not None:
                for mesg in msglist:
                    try:
                        qqinfo = QQInfo.objects.get(qq=qq)
                    except Exception as e:
                        qqinfo = None
                    if mesg['content'] is not '' and qqinfo:
                        create_time = datetime.datetime.fromtimestamp(int(mesg['created_time']))
                        address = 'name:'+mesg['lbs']['name']+'/'+'pos_x:'+mesg['lbs']['pos_x']+'/'+\
                                  'pos_y:'+mesg['lbs']['pos_y']
                        try:
                            emotion = EmotionInfo.objects.create(content=mesg['content'],
                                                                create_time=create_time,
                                                                address=address,
                                                                tools=mesg['source_name'],
                                                                publisher=qqinfo)
                            emotion.save()
                        except Exception as inserr:
                            message="insert emotion error"
                        else:
                            self.get_like(emotion.id, mesg, qq, name)
                            if mesg['cmtnum'] < 10:
                                if mesg['conlist'] is None:
                                    continue
                                self.get_comment(emotion.id, mesg, qq, name)
                            else:
                                params_more = {
                                    'uin': qq,
                                    'tid': mesg['tid'],
                                    'ftype': 0,
                                    'sort': 0,
                                    'pos': 0,
                                    'num': 20,
                                    't1_source': 'undefined',
                                    'callback': '_preloadCallback',
                                    'code_version': 1,
                                    'format': 'jsonp',
                                    'need_private_comment': 1,
                                    'g_tk': g_tk,
                                    'qzonetoken': self.cookie['g_qzonetoken']
                                }
                                url_more = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msgdetail_v6?'
                                url_more += urllib.parse.urlencode(params_more)
                                res_more = requests.get(url_more, headers=self.header, cookies=self.cookie)
                                res = re.findall('\((.*)\)', res_more.text, re.S)[0]
                                m_more = json.loads(res)
                                self.get_comment(emotion.id, m_more, qq, name)

            # # 如果没有说说就返回
            # for msglist in msg['msglist']:
            #     self.get_like(msglist, qq, name)
            #     if msglist['cmtnum'] < 10:
            #         if msglist['conlist'] is None:
            #             continue
            #         self.get_comment(msglist, qq, name)
            #     else:
            #         params_more = {
            #             'uin': qq,
            #             'tid': msglist['tid'],
            #             'ftype': 0,
            #             'sort': 0,
            #             'pos': 0,
            #             'num': 20,
            #             't1_source': 'undefined',
            #             'callback': '_preloadCallback',
            #             'code_version': 1,
            #             'format': 'jsonp',
            #             'need_private_comment': 1,
            #             'g_tk': g_tk,
            #             'qzonetoken': self.cookie['g_qzonetoken']
            #         }
            #         url_more = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msgdetail_v6?'
            #         url_more += urllib.parse.urlencode(params_more)
            #         res_more = requests.get(url_more, headers = self.header, cookies = self.cookie)
            #         res = re.findall('\((.*)\)', res_more.text, re.S)[0]
            #         m_more = json.loads(res)
            #         self.get_comment(m_more, qq, name)


    def get_denyfriend(self):
        deny_dir = os.path.join(BASE_DIR, 'static/conf/denyfriend.txt')
        with open(deny_dir, 'w') as f:
            f.write(json.dumps(self.denyfriend, ensure_ascii=False))

            # 得到的说说相关内容都在msglist(list类型)里面，msglist[i]是字典类型，可利用keys方法查看结构
            # 说说内容conlist[0]['con'],另外转发的说说在conlist[1/2/3....]
            # 每一条说说就是m
            # for m in msg['msglist']:
            #
            #     # 每一条说说下根据点赞计算关系值
            #     # self.cal_relationship_by_like(m, qq, name)
            #     # 记录共同好友点赞记录
            #     self.write_like(m, qq, name)
            #
            #     # 如果评论数大于10，则需要点进查看全部评论
            #     if m['cmtnum'] < 10:
            #         ##这里特殊，如果转发了说说并且没有配文字，而且原说说被删了，就会出现错误
            #         if m['conlist'] is None:
            #             continue
            #         self.write_comment(m, qq, name)
            #
            #     # 如果评论数大于10，则需要点进查看全部评论
            #     else:
            #         data_more = {
            #             'uin': qq,
            #             'tid': m['tid'],
            #             'ftype': 0,
            #             'sort': 0,
            #             'pos': 0,
            #             'num': 20,
            #             't1_source': 'undefined',
            #             'callback': '_preloadCallback',
            #             'code_version': 1,
            #             'format': 'jsonp',
            #             'need_private_comment': 1,
            #             'g_tk': g_tk,
            #         }
            #         url_more = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msgdetail_v6?'
            #         url_more += urllib.parse.urlencode(data_more)
            #         res_more = requests.get(url_more, headers=header, cookies=cookie)
            #         # print(url_more)
            #         # 匹配出_preloadCallback之后的内容
            #         r_more = re.findall('\((.*)\)', res_more.text)[0]
            #         # print(res_more.text)
            #         m_more = json.loads(r_more)
            #         # 写入txt文件
            #         self.write_comment(m_more, qq, name)

    def get_friend_img(self, friends):
        for friend in friends:
            img_url = 'http://qlogo.store.qq.com/qzone/'
            loc_url = os.path.join(BASE_DIR, 'static/images/qqimg/')
            img_url += friend.qq + '/' + friend.qq + '/' +'100'
            loc_url += friend.qq + '.png'
            r = requests.get(img_url)
            with open(loc_url, 'wb') as f:
                f.write(r.content)

#爬虫开始程序
def start_spider(request):
    count =0
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0",
        "Accepted-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    cookietxt_dir = os.path.join(BASE_DIR, 'static/conf/cookie_dic.txt')
    with open(cookietxt_dir, 'r') as f1:
        cookie = json.load(f1)
    f1.close()
    qzone = Qzone(cookie, header)
    qzone.get_friendlist(request)
    friends = QQInfo.objects.filter()
    # qzone.get_friend_img(friends)
    for i in friends:
        count+=1
        if i.id <= 48:
            continue
        if count % 4 == 0:
            sleep(30)
        qzone.get_emotion(i.qq, i.nick)
        qzone.get_denyfriend()
    return render(request, 'user/index.html')