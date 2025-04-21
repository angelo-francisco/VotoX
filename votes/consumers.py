import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Poll


class VoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        code = self.scope["url_route"]["kwargs"]["code"]
        poll = await self.aget_object_or_None(code)

        if self.scope["user"].is_authenticated and poll:
            self.poll = poll
            self.room = f"poll-{code}"

            await self.accept()

            await self.channel_layer.group_add(self.room, self.channel_name)

            await self.channel_layer.group_send(
                self.room,
                {"type": "user_update", "add": True},
            )
        else:
            await self.close()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room, self.channel_name)

        await self.channel_layer.group_send(
            self.room,
            {"type": "user_update", "remove": True},
        )

    async def user_update(self, event):
        if event.get("add", None):
            updated_voting_users_count = await self.update_voting_users_count(
                add=True
            )
        elif event.get("remove", None):
            updated_voting_users_count = await self.update_voting_users_count(
                remove=True
            )

        await self.send(
            text_data=json.dumps(
                {
                    "updated_voting_users_count": updated_voting_users_count,
                    "type": "user_update",
                }
            )
        )

    @database_sync_to_async
    def update_voting_users_count(self, add=None, remove=None):
        if (add and remove) or (not add and not remove):
            raise ValueError("Você deve passar apenas `add=True` ou `remove=True`.")

        if add:
            self.poll.voting_users_count += 1
        elif remove:
            self.poll.voting_users_count -= 1

        self.poll.save()

        return self.poll.voting_users_count

    @database_sync_to_async
    def aget_object_or_None(self, code):
        try:
            return Poll.objects.get(code=code)
        except Poll.DoesNotExist:
            return
