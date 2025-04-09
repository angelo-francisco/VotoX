from django.contrib import admin

from .models import User, VerificationCode

admin.site.register(User)
admin.site.register(VerificationCode)
