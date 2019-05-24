# qzoneinfo
## 爬取qq空间，并对qq空间进行数据分析
### 一共五个模块 登录注册、数据爬取、数据处理、数据分析、数据可视化

### 用到的技术有django、bootstrap、mysql，数据展示用到了echart3.0，数据处理方面用到了中文分词的结巴分词、然后通过对说说的关键字检索基于tf-idf算法算出相似度，好友关系网络中增加了无向图的连通分量对好友关系网络进行分类。

## 一共爬取了六万多条说说

### 登录界面
![登录](https://github.com/chunquansang/qzoneinfo/blob/master/displayimgs/login.png)
<img src="https://github.com/chunquansang/qzoneinfo/blob/master/login.png" width="150" height="150" alt="图片加载失败时，显示这段字"/>
<div align=center><img src="https://github.com/chunquansang/qzoneinfo/blob/master/displayimgs/login.png" width="300" height="450" /></div>
### 注册界面
![注册](https://github.com/chunquansang/qzoneinfo/blob/master/displayimgs/signup.png)
