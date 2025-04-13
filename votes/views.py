from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from .models import Poll, Comment

User = get_user_model()


def home_page(request):
    return render(request, "votes/home_page.html")


def pollings(request):
    polls = Poll.objects.filter(is_public=True)

    ctx = {"polls": polls}
    return render(request, "votes/pollings.html", ctx)


def poll_detail(request, username, poll_slug):
    owner = get_object_or_404(User, username=username)
    poll = get_object_or_404(Poll, created_by=owner, slug=poll_slug)
    comments = Paginator(Comment.objects.filter(poll=poll), 5).get_page(1)

    if hasattr("request", "htmx"):
        ...

    ctx = {
        "poll": poll,
        "owner": owner,
        "link": request.build_absolute_uri(),
        "comments": comments,
    }

    return render(request, "votes/poll_detail.html", ctx)


def manage_comments(request, poll_slug):
    from time import sleep

    poll = get_object_or_404(Poll, slug=poll_slug)
    comments = Paginator(Comment.objects.filter(poll=poll), 5)

    if request.method == "GET":
        get_next_page = request.GET.get("get_next_page", "").strip()
        get_previous_page = request.GET.get("get_previous_page", "").strip()

        if get_next_page:
            comments = comments.get_page(int(get_next_page))
        elif get_previous_page:
            comments = comments.get_page(int(get_previous_page))

    ctx = {"comments": comments, "poll": poll}

    return render(request, "partials/comments.html", ctx)
