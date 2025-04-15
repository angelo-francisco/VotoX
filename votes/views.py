from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comment, Poll, CategoryChoices, PollOption

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
    comments = Paginator(
        Comment.objects.filter(poll=poll).order_by("-created_at"), 5
    ).get_page(1)

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
    poll = get_object_or_404(Poll, slug=poll_slug)
    comments = Paginator(Comment.objects.filter(poll=poll).order_by("-created_at"), 5)

    if request.method == "GET":
        get_next_page = request.GET.get("get_next_page", "").strip()
        get_previous_page = request.GET.get("get_previous_page", "").strip()

        if get_next_page:
            comments = comments.get_page(int(get_next_page))
        elif get_previous_page:
            comments = comments.get_page(int(get_previous_page))

    if request.method == "POST" and request.user.is_authenticated:
        body = request.POST.get("comment", "").strip()

        if not body:
            ...
        else:
            Comment.objects.create(commented_by=request.user, poll=poll, body=body)
            comments = Paginator(
                Comment.objects.all().order_by("-created_at"), 5
            ).get_page(1)

    ctx = {"comments": comments, "poll": poll}

    return render(request, "partials/comments.html", ctx)


def new_poll(request):
    ctx = {}

    if request.method == "POST":
        cover = request.FILES.get("cover", "")
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "").strip()



    ctx["categories"] = CategoryChoices.choices
    return render(request, "votes/new_poll.html", ctx)
