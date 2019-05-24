from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class QQInfo(models.Model):
    qq = models.CharField(max_length=11, unique=True)
    nick = models.CharField(max_length=20)
    qqimg = models.CharField(max_length=256)

class EmotionInfo(models.Model):
    content = models.CharField(max_length=256)
    create_time = models.DateTimeField()
    address = models.CharField(max_length=50)
    tools = models.CharField(max_length=20)
    publisher = models.ForeignKey(QQInfo, on_delete=models.CASCADE)

class CommentInfo(models.Model):
    content = models.CharField(max_length=256)
    create_time = models.DateTimeField()
    from_qq = models.ForeignKey(QQInfo, on_delete=models.CASCADE, related_name='comment_fromqq')
    to_qq = models.ForeignKey(QQInfo, on_delete=models.CASCADE, related_name='comment_toqq')
    emotion = models.ForeignKey(EmotionInfo, on_delete=models.CASCADE)

class LikeInfo(models.Model):
    from_qq = models.ForeignKey(QQInfo, on_delete=models.CASCADE, related_name='like_fromqq')
    to_qq = models.ForeignKey(QQInfo,on_delete=models.CASCADE, related_name='like_toqq')
    emotion = models.ForeignKey(EmotionInfo,on_delete=models.CASCADE)


