from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import Poll, PollOption

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
