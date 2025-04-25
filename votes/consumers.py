import json

from channels.exceptions import DenyConnection, StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from redis import asyncio as aioredis

from django.conf import settings

from .repository import (
    check_poll,
    check_user,
    get_poll,
    get_option_percentage,
    vote_on_poll_option,
)


class VoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        code = self.scope["url_route"]["kwargs"]["code"]

        self.user = self.scope["user"]
        self.poll = await get_poll(code=code)

        if (not await check_poll(self.poll)) or not (await check_user(self.user)):
            raise DenyConnection(
                "Connection denied: invalid poll code or not allowed user"
            )

        self.room = f"answer_poll_room_{code}"
        self.redis_key = f"online_users:{code}"

        await self.accept()
        await self.channel_layer.group_add(self.room, self.channel_name)

        await self.mark_online()

        await self.broadcast_user_count()

    async def disconnect(self, close_code):
        await self.mark_offline()
        await self.broadcast_user_count()
        await self.channel_layer.group_discard(self.room, self.channel_name)
        raise StopConsumer("Consumer stop working completely")

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        match action:
            case "voting":
                option_id = data.get("optionId")

                if option_id.isdigit():
                    await self.vote_in_poll(int(option_id))

    async def vote_in_poll(self, option_id):
        option = await vote_on_poll_option(self.poll, option_id, self.user)

        if option:
            await self.channel_layer.group_send(
                self.room, {"type": "poll.update", "option_id": option.id}
            )

    async def poll_update(self, event):
        percentage = await get_option_percentage(self.poll, event["option_id"])

        await self.send(
            text_data=json.dumps(
                {
                    "type": "voting",
                    "optionId": event["option_id"],
                    "percentage": percentage,
                    "userId": self.user.id,
                }
            )
        )

    async def mark_online(self):
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.sadd(self.redis_key, self.user.id)
        await redis.expire(self.redis_key, 3600)

    async def mark_offline(self):
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.srem(self.redis_key, self.user.id)

    async def broadcast_user_count(self):
        redis = await aioredis.from_url(settings.REDIS_URL)
        count = await redis.scard(self.redis_key)

        await self.channel_layer.group_send(
            self.room,
            {
                "type": "user.count",
                "count": count,
            },
        )

    async def user_count(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_count",
                    "count": event["count"],
                }
            )
        )
