from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import PollCreationForm, PollOptionForm
from .models import Comment, Poll, PollOption, PollQuestion

User = get_user_model()


def home_page(request):
    return render(request, "votes/home_page.html")


def pollings(request):
    partialName = "partials/poll.html"
    flag = request.GET.get("flag", "")

    if flag == "all_polls":
        polls = Poll.objects.filter(is_public=True)
        ctx = {"polls": polls}

        return render(request, partialName, ctx)
    
    if flag == "my_polls":
        polls = Poll.objects.filter(created_by=request.user).order_by("-created_at")

        ctx = {"polls": polls}
        return render(request, partialName, ctx)

    polls = Poll.objects.filter(is_public=True)

    ctx = {"polls": polls}
    return render(request, "votes/pollings.html", ctx)


def poll_detail(request, username, poll_slug):
    owner = get_object_or_404(User, username=username)
    poll = get_object_or_404(Poll, created_by=owner, slug=poll_slug)
    comments = Paginator(
        Comment.objects.filter(poll=poll).order_by("-created_at"), 5
    ).get_page(1)

    ctx = {
        "poll": poll,
        "owner": owner,
        "link": request.build_absolute_uri(),
        "comments": comments,
    }

    return render(request, "votes/poll_detail.html", ctx)


@login_required
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

        if not body and request.headers.get("HX-Request"):
            messages.error(request, "Type some comment")
            return JsonResponse(
                {
                    "error": "Type some comment",
                    "messages": [
                        {"message": msg.message, "tags": msg.tags}
                        for msg in messages.get_messages(request)
                    ],
                }
            )
        else:
            Comment.objects.create(commented_by=request.user, poll=poll, body=body)
            comments = Paginator(
                Comment.objects.all().order_by("-created_at"), 5
            ).get_page(1)

    ctx = {"comments": comments, "poll": poll}

    return render(request, "partials/comments.html", ctx)


@login_required
def new_poll(request):
    if request.method == "POST":
        form = PollCreationForm(request.POST, request.FILES)
        options = PollOptionForm(request.POST)

        if form.is_valid() and options.is_valid():
            poll = form.save(commit=False)
            poll.created_by = request.user

            poll.save()

            options = options.get_options(request.POST)

            if len(options) < 2:
                messages.error(request, " You need to have 2 options by default")
                return redirect(reverse("new_poll"))

            PollOption.objects.bulk_create(
                [PollOption(poll=poll, option=option) for option in options]
            )

            messages.success(request, "New poll created")
            return redirect(reverse("new_poll"))
    else:
        form = PollCreationForm()
        options = PollOptionForm()

    ctx = {"options": options, "form": form}
    return render(request, "votes/new_poll.html", ctx)


@login_required
def go_poll(request):
    code = request.GET.get("code", "").strip()

    if code:
        poll = Poll.objects.filter(code=code).first()

        if poll and poll.is_active:
            return JsonResponse(
                {"msg": "Redirecting to the poll room...", "code": poll.code}
            )
        return JsonResponse({"msg": "Invalid or ended poll"}, status=400)

    return render(request, "votes/go_poll.html")


@login_required
def answer_poll(request, code):
    poll = get_object_or_404(Poll, code=code)
    options = get_list_or_404(PollOption, poll=poll)
    user_has_voted = poll.user_has_voted(request.user)
    questions = PollQuestion.objects.filter(poll=poll).order_by("-created_at")

    ctx = {
        "poll": poll,
        "options": options,
        "user_has_voted": user_has_voted,
        "questions": questions,
    }

    return render(request, "votes/answer_poll.html", ctx)


@login_required
def close_poll(request, code):
    poll = get_object_or_404(Poll, code=code)
    room = f"answer_poll_room_{poll.code}"

    if not poll.end_at and poll.created_by == request.user:
        poll.end_at = timezone.now()
        poll.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(room, {"type": "send.close.poll"})

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})
