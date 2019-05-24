from django.db import models

# Create your models here.

class User(models.Model):
    gender_desc = (
        ('male', '男'),
        ('female', '女'),
    )
    identify_desc= (
        ('user', '用户'),
        ('root', '管理员')
    )
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField()
    gender = models.CharField(max_length=10, choices=gender_desc, default='男')
    c_time = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=128, default='中国')
    birth = models.DateField(default='1991-01-01')
    identify = models.CharField(max_length=10, choices=identify_desc, default='用户')
    image = models.ImageField(upload_to='user', default='user/bochan50.png', verbose_name='头像')

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'