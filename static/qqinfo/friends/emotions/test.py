import jieba
from gensim import corpora,models,similarities
from collections import defaultdict
import os#用于创建一个空的字典，在后续统计词频可清理频率少的词语
from operator import itemgetter
from itertools import groupby
#1、读取文档
emotions_path = './'
L = []
similar_dic = {}

for root, dirs, files in os.walk(emotions_path):
    for file in files:
        if os.path.splitext(file)[1] == '.txt':
            L.append(os.path.splitext(file)[0])
for i in ['916920620']:
    becompared = []
    documents = []
    compare = i

    for j in L:
        if i != j:
            becompared.append(j)

    for i in becompared:
        doc = open(i+'.txt').read()
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
    d3 = open(compare+'.txt').read()

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

for key, value in similar_dic.items():
    a = max(value, key=itemgetter('sim'))
    print(a)