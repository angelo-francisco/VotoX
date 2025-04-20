from django.urls import path

from .consumers import VoteConsumer


websocket_url_patterns = [
    path('votes/', VoteConsumer.as_asgi())
]