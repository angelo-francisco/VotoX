from string import ascii_uppercase, digits

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()


class CategoryChoices(models.TextChoices):
    FOOD = "FD", "Food"
    TECHNOLOGY = "TI", "Technology"
    POLITICS = "PO", "Politics"
    SPORTS = "SP", "Sports"
    EDUCATION = "ED", "Education"
    ENTERTAINMENT = "EN", "Entertainment"
    HEALTH = "HE", "Health"
    TRAVEL = "TR", "Travel"
    ENVIRONMENT = "EV", "Environment"
    SCIENCE = "SC", "Science"
    BUSINESS = "BU", "Business"
    OTHER = "OT", "Other"


class Poll(models.Model):
    cover = models.ImageField(upload_to="polls_covers", null=True, blank=True)
    title = models.CharField(max_length=80)
    description = models.TextField()
    category = models.CharField(
        max_length=3,
        choices=CategoryChoices,
        default=CategoryChoices.OTHER,
    )
    is_public = models.BooleanField(default=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField(null=True, blank=True)
    max_votes = models.PositiveIntegerField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=False, null=True, blank=True)
    slug = models.SlugField(max_length=80, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0, null=True, blank=True)
    stars = models.ManyToManyField(User, related_name="stared_polls", blank=True)
    results_visible = models.BooleanField(default=True, null=True, blank=True)
    was_edited = models.BooleanField(default=False, null=True, blank=True)
    code = models.CharField(max_length=4, null=True, blank=True)
    voting_users_count = models.ManyToManyField(User, related_name="online_polls", blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.code:
            self.code = self.generate_unique_poll_code()

        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.end_at is None or self.end_at > timezone.now()


    @property
    def get_stars(self): ...

    @property
    def get_votes_count(self): ...

    def __str__(self):
        return self.title

    def generate_unique_poll_code(self):
        code = get_random_string(4, ascii_uppercase + digits)

        while Poll.objects.filter(code=code).exists():
            code = get_random_string(4, ascii_uppercase + digits)

        return code


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    option = models.CharField(max_length=200)
    votes = models.ManyToManyField(User)


class Comment(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="comments")
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
