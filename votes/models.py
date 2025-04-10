from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

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
    slug = models.SlugField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0, null=True, blank=True)
    stars = models.ManyToManyField(User, related_name="stared_polls")
    results_visible = models.BooleanField(default=True, null=True, blank=True)
    was_edited = models.BooleanField(default=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_active(self): ...

    @property
    def get_stars(self): ...

    @property
    def get_votes_count(self): ...


    def __str__(self):
        return self.title