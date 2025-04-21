import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Poll


class VoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        code = self.scope["url_route"]["kwargs"]["code"]
        poll = await self.aget_object_or_None(code)
        self.user = self.scope.get("user", None)

        if self.user and self.user.is_authenticated and poll:
            self.poll = poll
            self.room = f"poll-{code}"

            await self.accept()

            await self.channel_layer.group_add(self.room, self.channel_name)

            await self.channel_layer.group_send(
                self.room,
                {"type": "user_update"},
            )
        else:
            await self.close()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room, self.channel_name)

        await self.channel_layer.group_send(
            self.room,
            {"type": "user_update", "connecting": False},
        )

    async def user_update(self, event):
        voting_users_count = await self.update_voting_users_count(
            event.get("connecting", True)
        )

        await self.send(
            text_data=json.dumps(
                {
                    "updated_voting_users_count": voting_users_count,
                    "type": "user_update",
                }
            )
        )

    @database_sync_to_async
    def update_voting_users_count(self, connecting=True):
        is_user_on_the_poll = (
            True if self.poll.voting_users.filter(id=self.user.id).exists() else False
        )

        if not connecting and is_user_on_the_poll:
            self.poll.voting_users.remove(self.user)
            
        elif not is_user_on_the_poll and connecting:
            self.poll.voting_users.add(self.user)
            
        return self.poll.voting_users.count()

    @database_sync_to_async
    def aget_object_or_None(self, code):
        try:
            return Poll.objects.get(code=code)
        except Poll.DoesNotExist:
            return
