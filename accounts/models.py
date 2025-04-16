import string
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


class User(AbstractUser):
    profile_photo = models.ImageField(
        "Profile Photo", upload_to="profile_photos", null=True, blank=True
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class VerificationCode(models.Model):
    email = models.EmailField(null=True, blank=True, max_length=80)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    purpose = models.CharField(
        max_length=5, choices=(("VA", "Verify-Account"),), null=True, blank=True
    )

    @staticmethod
    def generate_code(length=6):
        code = get_random_string(length, string.ascii_uppercase + string.digits)

        while VerificationCode.objects.filter(code=code, is_used=False).exists():
            code = get_random_string(length, string.ascii_uppercase + string.digits)

        return code

    def is_valid(self):
        expiration_date = self.created_at + timedelta(minutes=5)
        return not self.is_used and timezone.now() <= expiration_date

    def mark_as_used(self):
        self.is_used = True
        self.save()
