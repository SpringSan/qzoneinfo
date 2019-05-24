# -*- coding: utf-8 -*-
# @Time    : 19-1-9 下午2:26
# @Author  : chunquansang
# @FileName: forms.py
# @Software: PyCharm

from django import forms

class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(label="密码", max_length=20, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    vcode = forms.CharField(label='验证码', max_length=4)