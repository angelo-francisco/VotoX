from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Poll, PollOption, PollQuestion

User = get_user_model()


@database_sync_to_async
def get_poll(**kwargs) -> Poll | None:
    """
    Try do get a poll by one or more atribs, and
    return None if there's not poll with that atribs
    """
    return Poll.objects.filter(**kwargs).first()


@database_sync_to_async
def check_poll(poll: Poll | None) -> bool:
    """
    Check if the poll exists and is valid
    """
    return bool(poll and poll.is_active)


@database_sync_to_async
def check_user(user: User) -> bool:  # type: ignore
    """
    Check if the user is authenticated and if him account
    """
    return user.is_authenticated and user.is_active


@database_sync_to_async
def has_end_at(poll: Poll):
    return poll.end_at is not None


@database_sync_to_async
def vote_on_poll_option(poll: Poll, option_id: int, user: User):  # type: ignore
    """
    Add user the a poll option and if user already vote return none
    """

    if poll.user_has_voted(user):
        return None

    option = poll.options.filter(id=option_id).first()

    if not option:
        return None

    option.votes.add(user)


@database_sync_to_async
def get_poll_options_statistics(poll: Poll):
    """
    Return the statistics of all options in the poll
    """

    options = PollOption.objects.filter(poll=poll)
    data = []

    for option in options:
        percentage = get_poll_option_percentage(poll, option.id)
        data.append((option.id, percentage))

    return data


@database_sync_to_async
def get_total_votes(poll: Poll):
    """
    Return the total of votes done in a poll
    """
    total_votes = 0
    options = PollOption.objects.filter(poll=poll)

    for option in options:
        total_votes += option.votes.count()

    return total_votes


def get_poll_option_percentage(poll: Poll, option_id: int):
    """
    Get the percentage vote of an option
    """
    option = PollOption.objects.filter(id=option_id).first()

    if not option:
        return None

    option_votes = option.votes.count()
    poll_options = PollOption.objects.filter(poll=poll)
    total_votes = 0

    for poll_option in poll_options:
        total_votes += poll_option.votes.count()

    return (round((option_votes * 100) / total_votes)) if total_votes else 0


@database_sync_to_async
def add_question(poll: Poll, body: str, user: User):  # type: ignore
    """
    Add a new poll question
    """
    question = PollQuestion.objects.create(poll=poll, author=user, body=body)

    return question


@database_sync_to_async
def get_user(**kwargs):
    """
    Get a user by the kwargs
    """
    return User.objects.filter(**kwargs).first()


@database_sync_to_async
def get_remaining_time(poll: Poll):
    """
    Return the remaining time to a poll
    """
    if not poll.end_at:
        return None

    now = timezone.now()

    if now >= poll.end_at:
        return "Encerrada"

    delta = poll.end_at - now
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"<span>{days}d:</span><span>{hours}h:</span><span>{minutes}m:</span><span>{seconds}s</span>"
    elif hours > 0:
        return f"<span>{hours}h:</span><span>{minutes}m:</span><span>{seconds}s</span>"
    else:
        return f"<span>{minutes}m:</span><span>{seconds}s</span>"



@database_sync_to_async
def try_closing_poll(poll: Poll, user: User):
    if not poll.end_at and poll.created_by == user:
        poll.end_at = timezone.now()
        poll.save()