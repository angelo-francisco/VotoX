from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import Poll

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
    return user.is_authenticated and user.is_active
