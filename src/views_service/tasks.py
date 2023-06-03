from celery import Celery
from src.views_service.views_manager import ViewsManager
import asyncio
from src.views_service.accounts_manager import AccountsManager


async def init_manager() -> AccountsManager:
    manager = await AccountsManager.create("accounts", "sessions")
    await manager.init()
    return manager

class ManagerInitiator:
    def __init__(self):
        self.manager = None

    def get_manager(self) -> AccountsManager:
        if self.manager is None:
            manager = asyncio.run(init_manager())
            self.manager = manager
        return self.manager

manager_init = ManagerInitiator()
celery_app = Celery("views", broker="redis://localhost:6379")

@celery_app.task
def view_channel(name: str, count: int, seconds: int):
    views_manager = ViewsManager(manager_init.get_manager())
    asyncio.run(views_manager.view_channel(name, count, seconds))
