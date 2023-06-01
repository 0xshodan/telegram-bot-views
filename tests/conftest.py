from src.accounts_manager import AccountsManager
import pytest_asyncio
import asyncio


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def manager():
    return await AccountsManager.create("accounts", "sessions")