from celery.utils.log import get_logger
from src.views_service.models import Task
import aiohttp
import asyncio

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
    def __init__(self) -> None:
        base_url = "http://app:8000"
        self.get_accounts_url = f"{base_url}/api/getAccounts"
        self.get_last_post_id_url = f"{base_url}/api/getLastPost"
        self.view_posts_url = f"{base_url}/api/viewPosts"

    async def _get(self, url: str, params: dict = {}, data=None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, data=data) as response:
                ret = await response.json()
        return ret
    async def _post(self, url: str, json: dict = {}) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json) as response:
                try:
                    ret = await response.json()
                except:
                    return None
        return ret
    async def get_accounts(self) -> list[str]:
        json = await self._get(self.get_accounts_url)
        return json["accounts"]

    async def view_posts(self, channel_name: str, account_id: str, posts:list[int]):
        await self._post(self.view_posts_url, json={
            "name": channel_name,
            "account_id": account_id,
            "posts": posts
            })

    async def get_last_post_id(self, channel_name: str) -> int:
        json = await self._get(self.get_last_post_id_url, {"name": channel_name})
        return json["id"]

    async def view_channel(self, channel_name: str, task_id: int, posts: list[int]):
        task = await Task.get(id=task_id)
        subtasks = task.body.split("\r\n")
        accounts = await self.get_accounts()
        offset = 0
        for subtask in subtasks:
            print(offset)
            count, view_time = subtask.split()
            count = int(count)
            if "ч" in view_time or "Ч" in view_time:
                vvtime = 3600 * int(view_time.replace("ч", "").replace("Ч", ""))
            elif "м" in view_time or "М" in view_time:
                vvtime = 60 * int(view_time.replace("м", "").replace("М", ""))
            elif "с" in view_time or "С" in view_time:
                vvtime = int(view_time.replace("с", "").replace("С", ""))
            else:
                vvtime = int(view_time)
            delay = vvtime / count
            print(offset, count)
            async for i in asyncrange(count):
                print("view")
                print(channel_name, accounts[offset+i], posts)
                await self.view_posts(channel_name, accounts[i], posts)
                await asyncio.sleep(delay)
            offset += count