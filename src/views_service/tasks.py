from src.views_service.main import celery_app
from src.views_service.views_manager import ViewsManager
import asyncio
from celery.utils.log import get_logger

logger = get_logger(__name__)


@celery_app.task
def view_channel(name: str, posts: list[int], task: dict):
    views_manager = ViewsManager()
    asyncio.run(views_manager.view_channel(name, task, posts))


# @celery_app.task
# def load_accounts():
#     manager = manager_init.get_manager()
#     asyncio.run(manager.add_accounts())


async def aiiter(q):
    return [i async for i in q]


@celery_app.task
def check_new_posts():
    views_manager = ViewsManager()
    print("task")
    channels = asyncio.run(views_manager.get_channels())
    print(channels)
    for channel in channels:
        last_post = asyncio.run(views_manager.get_last_post_id(channel["name"]))
        if last_post > channel["last_post_id"]:
            posts = [i for i in range(channel["last_post_id"] + 1, last_post + 1)]
            asyncio.run(views_manager.change_last_post_id(channel["name"], last_post))
            view_channel.delay(channel["name"], posts, channel["task"])
