import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Poll


class VoteConsumer(AsyncWebsocketConsumer):
    async def connect(self): ...

    async def disconnect(self, close_code): ...

    async def receive(self, text_data): ...
