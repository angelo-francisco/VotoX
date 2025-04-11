from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Poll

User = get_user_model()

def home_page(request):
    return render(request, 'votes/home_page.html')


def pollings(request):
    polls = Poll.objects.filter(is_public=True)

    ctx = {
        'polls': polls
    }
    return render(request, 'votes/pollings.html', ctx)

def poll_detail(request, username, poll_slug):
    owner = get_object_or_404(User, username=username)
    poll = get_object_or_404(Poll, created_by=owner, slug=poll_slug)


    ctx = {
        'poll': poll,
        'owner': owner
    }

    return render(request, 'votes/poll_detail.html', ctx)
    