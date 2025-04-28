from django.urls import path

from .views import (
    answer_poll,
    go_poll,
    home_page,
    manage_comments,
    new_poll,
    poll_detail,
    pollings,
    close_poll
)

urlpatterns = [
    path("", home_page, name="home_page"),
    path("pollings/", pollings, name="pollings"),
    path("new/", new_poll, name="new_poll"),
    path("go/", go_poll, name="go_poll"),
    path("close-poll/<code>/", close_poll,name="close_poll"),
    path("manage-comments/<poll_slug>/", manage_comments, name="manage_comments"),
    path("@<username>/<poll_slug>/", poll_detail, name="poll_detail"),
    path("<code>/", answer_poll, name="answer_poll"),
]
