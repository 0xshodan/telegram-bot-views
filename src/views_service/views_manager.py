from telethon.tl.functions.messages import GetMessagesViewsRequest
import random
from .accounts_manager import AccountsManager, TelegramAccount
import asyncio
from celery.utils.log import get_logger


logger = get_logger(__name__)
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
        logger.info(client)
        messages = client.iter_messages(channel_name)
        logger.info(messages)
        message_id = [i async for i in messages][0].id
        logger.info(message_id)
        return message_id

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
        logger.info(delay)
        last_post_id = [await self.get_last_post_id(channel_name)]
        logger.info(views_count)
        async for i in asyncrange(views_count):
            await self.view_posts(channel_name, last_post_id, self.accounts_manager.accounts[i])
            logger.info(f"delay: {delay}")
            await asyncio.sleep(delay)