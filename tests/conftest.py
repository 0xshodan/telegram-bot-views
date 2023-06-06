from src.views_service.accounts_manager import AccountsManager
import pytest_asyncio
import asyncio
from tortoise import Tortoise

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def tortoise():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['src.views_service.models']}
    )
    await Tortoise.generate_schemas()


@pytest_asyncio.fixture(scope="session")
async def manager():
    return await AccountsManager.create()