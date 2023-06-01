import pytest
from src.views_manager import ViewsManager

@pytest.mark.asyncio
async def test_views(manager):
    views_manager = ViewsManager(manager)
    await views_manager.view_channel("@sspertest", 2, 20)
    print("viewed")
    await views_manager.view_channel("@mysupertestchannels", 2, 10)