from django.shortcuts import render

# Create your views here.
from qqinfo.models import QQInfo, EmotionInfo, LikeInfo, CommentInfo
import os
from qzoneinfo.settings import BASE_DIR
import jieba
from collections import Counter
from django.http.response import HttpResponse
import re
from wordcloud import WordCloud
from matplotlib import pyplot
from collections import OrderedDict
import pyecharts
from qzoneinfo.settings import AK, SK
from urllib import parse
import hashlib
import requests
import json
from tools.views import page_to_page
from gensim import corpora, models, similarities
from collections import defaultdict
from operator import itemgetter


def emotions_db_to_text(request):
    emotions = EmotionInfo.objects.filter()
    emotions_path = os.path.join(BASE_DIR, 'static/qqinfo/friends/processedtext/emotionstext.txt')
    for emotion in emotions:
        emotion_path = os.path.join(BASE_DIR, 'static/qqinfo/friends/emotions/')
        emotion_path += emotion.publisher.qq + '.txt'
        seg_words = seg_sentence(emotion.content)
        with open(emotion_path, 'a') as f:
            f.write(seg_words)
        with open(emotions_path, 'a') as f1:
            f1.write(seg_words)
    return HttpResponse('ok')

def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r').readlines()]
    return stopwords


# 对句子进行分词
def seg_sentence(sentence):
    stop_words_path = os.path.join(BASE_DIR, 'static/conf/stop_words.txt')
    sentence_seged = jieba.cut(sentence.strip())
    stopwords = stopwordslist(stop_words_path)  # 这里加载停用词的路径
    outstr = ''
    for word in sentence_seged:
        if word.isdigit() or word.isspace():
            continue
        if re.search("^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]{6,20})$",word) is not None:
            continue
        if word.startswith('e'):
            continue
        if word not in stopwords:
            if word != '\t':
                outstr += word
                outstr += " "
    return outstr

def create_word_cloud(request):
    tff_path = os.path.join(BASE_DIR, 'static/fonts/simfang.ttf')
    emotions_path = os.path.join(BASE_DIR, 'static/qqinfo/friends/processedtext/emotionstext.txt')
    cloud_img_path = os.path.join(BASE_DIR, 'static/images/analysis/cloud.png')
    wl = ''
    with open(emotions_path, 'r') as f:
        wl=f.read()
    wc = WordCloud(
        # 设置背景颜色
        background_color="white",
        # 设置最大显示的词云数
        max_words=2000,
        font_path=tff_path,
        height=800,
        width=1200,
        # 设置字体最大值
        max_font_size=100,
        # 设置有多少种随机生成状态，即有多少种配色方案
        random_state=30,
    )
    mycloud = wc.generate(wl)
    pyplot.imshow(mycloud)
    pyplot.axis("off")
    pyplot.show()
    wc.to_file(cloud_img_path)

    try:
        friends = QQInfo.objects.filter()
    except Exception as e:
        message = '读取好友失败'
    else:
        data, friend_list = page_to_page(request, 10, friends)
    return render(request, 'analysis/cloudword.html',{
        'data': data,
        'friend_list': friend_list,
    })

def create_friend_emotion_fea(request):
    if request.method == 'GET':
        master = request.session.get('qq')
        qq = request.GET.get('qq', '')
        friend = QQInfo.objects.get(qq=qq)
        year_counts = OrderedDict()
        for year in range(2010, 2020):
            emotion_year = EmotionInfo.objects.filter(create_time__year=str(year)).\
                filter(publisher_id=friend.id)
            yearcount = len(emotion_year)
            year_counts[str(year)] = yearcount
        year_tag = list(year_counts.keys())
        year_count_tag = list(year_counts.values())
        hour_counts = OrderedDict()
        day_counts = {}
        emotions = EmotionInfo.objects.filter(publisher_id=friend.id)
        for emotion in emotions:
            emotion_hour = emotion.create_time.hour
            for hour in range(0, 24):
                if str(hour) not in hour_counts:
                    hour_counts[str(hour)] = 0
                if emotion_hour == hour:
                    hour_counts[str(hour)] += 1
            emotion_day = emotion.create_time.date()
            if emotion_day in day_counts:
                day_counts[emotion_day] += 1
            else:
                day_counts[emotion_day] = 0
                day_counts[emotion_day] += 1
        max_sort = 10
        L = sorted(day_counts.items(), key = lambda item: item[1], reverse=True)
        L = L[:max_sort]
        days_count = {}
        for l in L:
            days_count[l[0].strftime('%Y-%m-%d')] = l[1]
        day_tag = list(days_count.keys())
        day_count_tag = list(days_count.values())
        hour_tag = list(hour_counts.keys())
        hour_count_tag = list(hour_counts.values())
        try:
            friends = QQInfo.objects.filter()
        except Exception as e:
            message = '读取好友失败'
        else:
            data, friend_list = page_to_page(request, 10, friends)
        similar_path = os.path.join(BASE_DIR, 'static/conf/similar.txt')
        with open(similar_path, 'r') as f:
            similar_friend = json.load(f)
        print(type(similar_friend))
        similarest_friend = ''
        if qq in similar_friend:
            similarest_friend = QQInfo.objects.get(qq=similar_friend[qq])
        return render(request, 'analysis/friendfea.html', {'year_tag': year_tag,
                                                           'year_count_tag': year_count_tag,
                                                           'hour_tag': hour_tag,
                                                           'hour_count_tag': hour_count_tag,
                                                           'day_tag': day_tag,
                                                           'similarest_friend': similarest_friend,
                                                           'day_count_tag': day_count_tag,
                                                           'friend_list': friend_list,
                                                           'qq': master,
                                                           'data': data,
                                                           'friend_qq': friend,
                                                           })

def create_friend_tools_fea(request):
    friends = QQInfo.objects.all()
    tools_info = {}
    tools_brand = {}
    for friend in friends:
        emotions = EmotionInfo.objects.filter(publisher_id=friend.id).exclude(tools='')\
        .exclude(tools='手机QQ').exclude(tools='QQ空间触屏版').exclude(tools='情侣空间')
        for emotion in emotions:
            if friend.nick not in tools_info:
                tools_info[friend.nick] = [emotion.tools]
            else:
                if emotion.tools not in tools_info[friend.nick]:
                    tools_info[friend.nick].append(emotion.tools)

                    tool_brand = judge_tools_version(emotion.tools)
                    if tools_brand is not None:
                        if tool_brand not in tools_brand:
                            tools_brand[tool_brand] = 0
                            tools_brand[tool_brand] += 1
                        else:
                            tools_brand[tool_brand] += 1
    brand_tag = list(tools_brand.keys())
    max_sort = 20
    L = sorted(tools_info.items(), key=lambda item: len(item[1]), reverse=True)
    L = L[:max_sort]
    tools_change_count = {}
    for l in L:
        tools_change_count[l[0]] = len(l[1])
    user_tag = list(tools_change_count.keys())
    tools_count_tag = list(tools_change_count.values())
    try:
        friends = QQInfo.objects.filter()
    except Exception as e:
        message = '读取好友失败'
    else:
        data, friend_list = page_to_page(request, 10, friends)
    return render(request, 'analysis/toolsfea.html', {
        'brands': tools_brand,
        'brand_tag': brand_tag,
        'user_tag': user_tag,
        'tools_count_tag': tools_count_tag,
        'data': data,
        'friend_list': friend_list,
    })

'''
    判断设备的型号
'''
def judge_tools_version(tools):
    tool = tools.lower()
    ref_tools = {
        'iPhone': ['ipad', 'ipod', 'iphone', ],
        'alps': ['alps'],
        '小米': ['小米', 'mi note', 'xiaomi', '红米'],
        '三星': ['三星', 'galaxy', 'gt-s6500d', 'samsung', 'sm-a5100'],
        '谷歌': ['google', 'nexus', '谷歌'],
        '海信': ['hisense', '海信'],
        'htc': ['htc'],
        '华为': ['huawei', '华为', '荣耀'],
        'lvvi': ['lvvi'],
        '联想': ['lenovo', '联想'],
        '魅族': ['meizu', '魅族', '魅蓝'],
        '努比亚': ['nubia', '努比亚', 'z9 max'],
        'oppo': ['oppo'],
        '坚果': ['smartisan', '坚果'],
        'sony': ['sony'],
        'vivo': ['vivo'],
        '中兴': ['中兴'],
        '乐视': ['乐max', '乐max2'],
        '天语': ['天语'],
        '金立s': ['金立'],
        'andriod': ['android'],
        'windowsphone': ['windows phone'],
        '展讯': ['展讯'],
        '酷派': ['酷派', 'coolpad'],
        '朵唯': ['朵唯'],
        '一加': ['oneplus'],
    }
    for ref_tool in ref_tools.items():
        for i in ref_tool[1]:
            if i in tool:
                return ref_tool[0]
    print(tools)

def create_emotion_fea(request):
    year_counts = OrderedDict()
    for year in range(2010, 2020):
        emotion_year = EmotionInfo.objects.filter(create_time__year=str(year))
        yearcount = len(emotion_year)
        year_counts[str(year)] = yearcount
    year_tag = list(year_counts.keys())
    year_count_tag = list(year_counts.values())
    hour_counts = OrderedDict()
    emotions = EmotionInfo.objects.filter()
    for emotion in emotions:
        emotion_hour = emotion.create_time.hour
        for hour in range(0, 24):
            if str(hour) not in hour_counts:
                hour_counts[str(hour)] = 0
            if emotion_hour == hour:
                hour_counts[str(hour)] += 1
    hour_tag = list(hour_counts.keys())
    hour_count_tag = list(hour_counts.values())
    emotions_address = EmotionInfo.objects.exclude(address='')
    address_dic = {}
    address_count = {}
    for emotion_address in emotions_address:
        address = emotion_address.address
        address_proc = address.split('/')[0]
        pos_y = address.split('/')[1]
        pos_x = address.split('/')[2]
        pos = []
        pos.append(float(pos_x))
        pos.append(float(pos_y))
        address_dic[address_proc] = pos
        if address_proc not in address_count:
            address_count[address_proc] = 0
            address_count[address_proc] += 1
        else:
            address_count[address_proc] += 1
        try:
            friends = QQInfo.objects.filter()
        except Exception as e:
            message = '读取好友失败'
        else:
            data, friend_list = page_to_page(request, 10, friends)

    return render(request, 'analysis/emotionsfea.html', {
        'year_tag': year_tag,
        'year_count_tag': year_count_tag,
        'hour_tag': hour_tag,
        'hour_count_tag': hour_count_tag,
        'address_tag': address_dic,
        'address_count_tag': address_count,
        'data': data,
        'friend_list': friend_list,
    })



def get_url(location):
    queryStr = '/geocoder/v2/?location=%s&output=json&ak=%s' % (location, AK)
    # 对queryStr进行转码，safe内的保留字符不转换
    encodedStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    # 在最后直接追加上yoursk
    rawStr = encodedStr + SK
    # 计算sn
    sn = (hashlib.md5(parse.quote_plus(rawStr).encode("utf8")).hexdigest())
    # 由于URL里面含有中文，所以需要用parse.quote进行处理，然后返回最终可调用的url
    url = parse.quote("http://api.map.baidu.com" + queryStr + "&sn=" + sn, safe="/:=&?#+!$,;'@()*[]")
    return url

def location_to_address(request):
    emotions = EmotionInfo.objects.exclude(address='')
    for emotion in emotions:
        address = emotion.address
        address_pro = address.split('/')
        pos_x = address_pro[2]
        pos_y = address_pro[1]
        pos_x = pos_x.split(':')[1]
        pos_y = pos_y.split(':')[1]
        location = pos_x + ',' +pos_y
        url = get_url(location)
        r = requests.get(url)
        result = r.json()
        print(result)
        city = result['result']['addressComponent']['city']
        province = result['result']['addressComponent']['province']
        district = result['result']['addressComponent']['district']
        if district == '':
            result_address = province + city
        else:
            result_address = province+city+district
        print(result_address)
        emotion_address = result_address + '/' +pos_x + '/' + pos_y
        emotion.address = emotion_address
        emotion.save()
    return HttpResponse('ok')

def comment_like_to_text(request):
    calrelationship_path = os.path.join(BASE_DIR, 'static/conf/calrelationship.txt')
    comments = CommentInfo.objects.all()
    relationship_dic = {}
    for comment in comments:
        from_nick = comment.from_qq.nick
        to_nick = comment.to_qq.nick
        if from_nick == to_nick:
            continue
        from_to = from_nick+'$|$'+to_nick
        print(from_to)
        if from_to not in relationship_dic:
            relationship_dic[from_to] = 0
            relationship_dic[from_to] += 3
        else:
            relationship_dic[from_to] += 3
    likes = LikeInfo.objects.all()
    for like in likes:
        from_nick = like.from_qq.nick
        to_nick = like.to_qq.nick
        if from_nick == to_nick:
            continue
        from_to = from_nick+'$|$'+to_nick
        print(from_to)
        if from_to not in relationship_dic:
            relationship_dic[from_to] = 0
            relationship_dic[from_to] += 1
        else:
            relationship_dic[from_to] += 1
    for key, value in relationship_dic.items():
        with open(calrelationship_path, 'a') as f:
            content = key + '$|$' + str(value)
            f.write(content)
            f.write('\n')
    return HttpResponse('ok')

def create_relationship_fea(request):
    calrelationship_path = os.path.join(BASE_DIR, 'static/conf/calrelationship.txt')
    from_nick = []
    to_nick = []
    weight = []
    nodes = {}
    nodes_new = {}
    relationship = {}
    with open(calrelationship_path, 'r') as f:
        line = f.readline()
        line = line.strip('\n')
        from_nick.append(line.split('$|$')[0])
        to_nick.append(line.split('$|$')[1])
        weight.append(line.split('$|$')[2])
        while line:
            line = f.readline()
            if line:
                line = line.strip('\n')
                from_nick.append(line.split('$|$')[0])
                to_nick.append(line.split('$|$')[1])
                weight.append(line.split('$|$')[2])
    from_to = from_nick+to_nick
    id = 0
    for i in from_to:
        if i not in nodes_new:
            nodes_new[i] = id
            id+=1
    for key, value in nodes_new.items():
        nodes[value] = key
    for (i, j, k) in zip(from_nick, to_nick, weight):
        from_id = nodes_new[i]
        to_id = nodes_new[j]
        if from_id not in relationship:
            relationship[from_id] = {}
            relationship[from_id][to_id] = int(k)
        else:
            if to_id in relationship[from_id]:
                relationship[from_id][to_id] += int(k)
            else:
                relationship[from_id][to_id] = int(k)

    graph = {}
    for key, value in relationship.items():
        graph[key] = set(relationship[key].keys())
        for i in relationship[key].keys():
            if i not in graph:
                graph[i] = set()
                graph[i].add(key)
            else:
                graph[i].add(key)
    for key, value in relationship.items():
        for i in relationship[key].keys():
            if i not in graph:
                graph[i] = set()
                graph[i].add(key)
            else:
                graph[i].add(key)
    graph[273] = {274,}
    graph[274] = {273,}
    nodes[273] = "sa"
    nodes[274] = "da"
    def walk(G, s, S=set()):
        P, Q = dict(), set()
        P[s] = None  # s节点没有前任节点
        Q.add(s)  # 从s开始搜索
        while Q:
            u = Q.pop()
            for v in G[u].difference(P, S):  # 得到新节点
                Q.add(v)
                P[v] = u  # 记录前任节点
        return P

    def components(G):
        comp = []
        seen = set()
        for u in G.keys():
            if u in seen:
                continue
            C = walk(G, u)
            seen.update(C)
            comp.append(C)
        return comp

    N = {
        0:{1,2},
        1:{0},
        2:{0},
        3:{4},
        4:{3}
    }
    comp = components(graph)
    for j in relationship:
        for k in relationship[j]:
            relationship[j][k] = 1 if(int(int(relationship[j][k])/500)<1) else int(int(relationship[j][k])/10)
    relanode = {}
    for i in range(0,len(comp)):
        for key, value in comp[i].items():
           if key in nodes:
               relanode[key] = {'name': nodes[key], 'catagory': i}
           if value is not None and value in nodes:
               relanode[value] = {'name': nodes[value], 'catagory': i}
    relanode = dict(sorted(relanode.items(), key=lambda item:item[0]))
    try:
        friends = QQInfo.objects.filter()
    except Exception as e:
        message = '读取好友失败'
    else:
        data, friend_list = page_to_page(request, 10, friends)
    source = []
    target= []
    wei = []
    for i in relationship:
        for j in relationship[i]:
            source.append(i)
            target.append(j)
            wei.append(relationship[i][j])
    reladata = zip(source, target, wei)
    return render(request, 'analysis/relationshipfea.html', {
        'nodes': relanode,
        'relationship': relationship,
        'components': comp,
        'data': data,
        'reladata': reladata,
        'friend_list': friend_list,
    })

def test(request):
    return render(request, 'analysis/friendfea.html')

def create_deny_fea(request):
    deny_path = os.path.join(BASE_DIR, 'static/conf/denyfriend.txt')
    with open(deny_path, 'r') as f:
        deny_friends = json.load(f)
    try:
        friends = QQInfo.objects.filter()
    except Exception as e:
        message = '读取好友失败'
    else:
        data, friend_list = page_to_page(request, 10, friends)
    return render(request, 'analysis/denyfriends.html', {
        'data': data,
        'friend_list': friend_list,
        'deny_friends': deny_friends
    })

def similarity_cal():
    emotions_path = os.path.join(BASE_DIR, 'static/qqinfo/friends/emotions/')
    L = []
    similar_dic = {}
    similar_friend = {}
    similar_max = {}
    for root, dirs, files in os.walk(emotions_path):
        for file in files:
            if os.path.splitext(file)[1] == '.txt':
                L.append(os.path.splitext(file)[0])
    aa=0
    for i in L:
        becompared = []
        documents = []
        compare = i

        for j in L:
            if i != j:
                becompared.append(j)

        for i in becompared:
            doc = open(emotions_path+i + '.txt').read()
            documents.append(doc)

        texts = [[word for word in document.split(' ')] for document in documents]
        # 4、 计算词语的频率
        frequency = defaultdict(int)
        for text in texts:
            for word in text:
                frequency[word] += 1
        '''
        #5、对频率低的词语进行过滤（可选）
        texts=[[word for word in text if frequency[word]>10] for text in texts]
        '''
        # 6、通过语料库将文档的词语进行建立词典
        dictionary = corpora.Dictionary(texts)
        # 7、加载要对比的文档
        d3 = open(emotions_path+compare + '.txt').read()

        # 8、将要对比的文档通过doc2bow转化为稀疏向量
        new_xs = dictionary.doc2bow(d3.split(' '))
        # 9、对语料库进一步处理，得到新语料库
        corpus = [dictionary.doc2bow(text) for text in texts]
        # 10、将新语料库通过tf-idf model 进行处理，得到tfidf
        tfidf = models.TfidfModel(corpus)
        # 11、通过token2id得到特征数
        featurenum = len(dictionary.token2id.keys())
        # 12、稀疏矩阵相似度，从而建立索引
        index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=featurenum)
        # 13、得到最终相似结果
        sim = index[tfidf[new_xs]]
        similar_dic[compare] = []
        for k in range(len(sim)):
            print('%s 与 %s 相似度为：%.2f' % (compare, becompared[k], sim[k]))
            similar_dic[compare].append({'becompared': becompared[k], 'sim': sim[k]})

        print(aa)
        aa+=1
    for key, value in similar_dic.items():
        similar_max = max(value, key=itemgetter('sim'))
        similar_friend[key] = similar_max['becompared']
    print(similar_friend)
    similar_path = os.path.join(BASE_DIR, 'static/conf/similar.txt')
    with open(similar_path, 'w') as f:
        json.dump(similar_friend, f)

def create_similarity_cal(request):
    similarity_cal()

    return HttpResponse('ok')

def create_popularest_emotion(request):
    popular_emotion = {}
    comments = CommentInfo.objects.all()
    for comment in comments:
        if comment.emotion_id not in popular_emotion:
            popular_emotion[comment.emotion_id] = 0
            popular_emotion[comment.emotion_id] += 3
        else:
            popular_emotion[comment.emotion_id] += 3
    likes = LikeInfo.objects.all()
    for like in likes:
        if like.emotion_id not in popular_emotion:
            popular_emotion[like.emotion_id] = 0
            popular_emotion[like.emotion_id] += 1
        else:
            popular_emotion[like.emotion_id] += 1
    print(popular_emotion)
    popular_emotion_id = max(popular_emotion, key=popular_emotion.get)
    emotion = EmotionInfo.objects.get(id = popular_emotion_id)
    try:
        friends = QQInfo.objects.filter()
    except Exception as e:
        message = '读取好友失败'
    else:
        data, friend_list = page_to_page(request, 10, friends)
    return render(request, 'analysis/popularestemotion.html', {
        'data': data,
        'friend_list': friend_list,
        'popularest': emotion,
    })