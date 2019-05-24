from django.contrib import admin
from user.models import User

# Register your models here.

from user import models

class UserAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id', 'username', 'email', 'gender', 'address', 'birth', 'c_time', 'identify']
admin.site.register(User, UserAdmin)