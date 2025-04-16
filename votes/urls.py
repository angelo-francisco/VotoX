from django.urls import path

from .views import home_page, manage_comments, new_poll, poll_detail, pollings

urlpatterns = [
    path("", home_page, name="home_page"),
    path("pollings/", pollings, name="pollings"),
    path("@<username>/<poll_slug>/", poll_detail, name="poll_detail"),
    path("new-poll/", new_poll, name="new_poll"),
    path("manage-comments/<poll_slug>/", manage_comments, name="manage_comments"),
]
