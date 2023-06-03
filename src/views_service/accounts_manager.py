from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import UseCurrentSession, APIData
from src.views_service.models import Client, Proxy
from src.views_service.models import Account as AccountModel


def split_chucks(list_a: list, chunk_size: int) -> list:

  for i in range(0, len(list_a), chunk_size):
    yield list_a[i:i + chunk_size]

class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class AccountsManager(metaclass=SingletonMeta):

    @classmethod
    async def create(cls):
        self = AccountsManager()
        try:
            if self.clients == []:
                self.clients: list[TelegramClient] = await self.load_clients()
        except AttributeError:
            self.clients: list[TelegramClient] = await self.load_clients()
        return self

    async def load_clients(self) -> list[TelegramClient]:
        _clients: list[TelegramClient] = []
        clients_db = await Client.all()

        for client_db in clients_db:
            api = APIData.Generate(client_db.unique_id)
            tdesk = TDesktop(api=api)
            for account in client_db.accounts:
                tdesk.LoadTData(account.tdata_path)
            client = await tdesk.ToTelethon(
                session=client_db.session,
                flag=UseCurrentSession,
                proxy=client_db.proxy.to_socks()
                )
            _clients.append(client)
        _clients += self._load_unloaded()
        return _clients


    async def _load_unloaded(self) -> list[TelegramClient]:
        _clients: list[TelegramClient] = []
        unloaded_accs = await AccountModel.filter(unloaded=True)
        for unloaded in split_chucks(unloaded_accs, 3):
            client_db = Client.create()
            print(client_db)
            api = APIData.Generate(client_db.unique_id)
            tdesk = TDesktop(api=api)
            for account in unloaded:
                tdesk.LoadTData(account.tdata_path)
            client = await tdesk.ToTelethon(
                session=client_db.session,
                flag=UseCurrentSession,
                proxy=Proxy.get_available().to_socks()
                )
            _clients.append(client)
        return _clients


    async def init(self):
        for i in range(len(self)):
            await self.clients[i].connect()

    def __len__(self) -> int:
        return len(self.accounts)
