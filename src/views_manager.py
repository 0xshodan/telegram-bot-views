from telethon.tl.functions.messages import GetMessagesViewsRequest
import random
from .accounts_manager import AccountsManager, TelegramAccount
import asyncio


class asyncrange:

    class __asyncrange:
        def __init__(self, *args):
            self.__iter_range = iter(range(*args))

        async def __anext__(self):
            try:
                return next(self.__iter_range)
            except StopIteration as e:
                raise StopAsyncIteration(str(e))

    def __init__(self, *args):
        self.__args = args

    def __aiter__(self):
        return self.__asyncrange(*self.__args)


class ViewsManager:

    def __init__(self, accounts_manager: AccountsManager):
        self.accounts_manager = accounts_manager

    async def get_last_post_id(self, channel_name: str):
        client = random.choice(self.accounts_manager.accounts).account
        return [i async for i in client.iter_messages(channel_name)][0].id

    async def view_posts(self, channel_name: str, post_ids: list[int], worker: TelegramAccount):
        await worker.account(
            GetMessagesViewsRequest(
                peer=channel_name,
                id=post_ids,
                increment=True
            )
        )

    async def view_channel(self, channel_name: str, views_count: int, seconds: int):
        delay = seconds / views_count
        last_post_id = [await self.get_last_post_id(channel_name)]
        async for i in asyncrange(views_count):
            await self.view_posts(channel_name, last_post_id, self.accounts_manager.accounts[i])
            await asyncio.sleep(delay)