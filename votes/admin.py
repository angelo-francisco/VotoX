from django.contrib import admin

from .models import Poll, Comment

admin.site.register(Poll)
admin.site.register(Comment)