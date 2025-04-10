from django.urls import path
from .views import (
    home_page,
    pollings
)

urlpatterns = [
    path('', home_page, name="home_page"),
    path("pollings/", pollings, name="pollings")
]
