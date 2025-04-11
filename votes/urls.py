from django.urls import path
from .views import (
    home_page,
    pollings,
    poll_detail,
)

urlpatterns = [
    path('', home_page, name="home_page"),
    path("pollings/", pollings, name="pollings"),
    path("@<username>/<poll_slug>/", poll_detail, name="poll_detail")
]
