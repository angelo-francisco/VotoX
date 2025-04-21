from django.urls import path

from .consumers import VoteConsumer


websocket_url_patterns = [
    path('vote/<code>/', VoteConsumer.as_asgi())
]