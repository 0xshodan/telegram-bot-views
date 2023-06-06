import pytest
from src.views_service.views_manager import ViewsManager
from src.views_service.models import Channel


@pytest.mark.asyncio
async def test_views(tortoise, manager):
    views_manager = ViewsManager(manager)
    channel = (await Channel.all())[0]
    task = await channel.task.all()
    await views_manager.view_channel(channel.name, task, [3,4])