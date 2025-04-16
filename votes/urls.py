from django.urls import path

from .views import go_poll, home_page, manage_comments, new_poll, poll_detail, pollings

urlpatterns = [
    path("", home_page, name="home_page"),
    path("pollings/", pollings, name="pollings"),
    path("new/", new_poll, name="new_poll"),
    path("go/", go_poll, name="go_poll"),
    path("@<username>/<poll_slug>/", poll_detail, name="poll_detail"),
    path("manage-comments/<poll_slug>/", manage_comments, name="manage_comments"),
]
