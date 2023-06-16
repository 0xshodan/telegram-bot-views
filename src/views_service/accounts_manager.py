from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import UseCurrentSession, API
from src.views_service.models import Proxy
from src.views_service.models import Account as AccountModel
from dataclasses import dataclass
from telethon.tl.functions.messages import GetMessagesViewsRequest
import random
from telethon.errors.rpcerrorlist import SessionRevokedError, AuthKeyUnregisteredError


def split_chucks(list_a: list, chunk_size: int) -> list:

  for i in range(0, len(list_a), chunk_size):
    yield list_a[i:i + chunk_size]

@dataclass
class AccountClient:
    id: str
    client: TelegramClient

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
        clients_db = await AccountModel.all()

        for client_db in clients_db:
            if client_db.unloaded:
                proxy = await Proxy.get_available()
                client_db.proxy = proxy
                client_db.unloaded = False
                client_db.session = f"sessions/uid{client_db.unique_id}.session"
                await client_db.save()
            else:
                proxy = await client_db.proxy.all()
            api = API.TelegramIOS.Generate(client_db.unique_id)
            try:
                tdesk = TDesktop(api=api, basePath=client_db.tdata_path)
                client = await tdesk.ToTelethon(
                session=client_db.session,
                flag=UseCurrentSession,
                proxy=proxy.to_socks()
                )
                _clients.append(AccountClient(str(client_db.unique_id), client))
            except Exception as ex:
                print(ex)
                print(client_db.tdata_path)
                print(client_db.unique_id)
                continue
        return _clients

    async def add_accounts(self):
        _clients: list[TelegramClient] = []
        clients_db = await AccountModel.filter(unloaded=True)
        for client_db in clients_db:
            proxy = await Proxy.get_available()
            client_db.proxy = proxy
            client_db.unloaded = False
            client_db.session = f"sessions/uid{client_db.unique_id}.session"
            await client_db.save()
            api = API.TelegramIOS.Generate(client_db.unique_id)
            tdesk = TDesktop(api=api, basePath=client_db.tdata_path)
            client = await tdesk.ToTelethon(
                session=client_db.session,
                flag=UseCurrentSession,
                proxy=proxy.to_socks()
                )
            _clients.append(AccountClient(str(client_db.unique_id), client))
        self.clients += _clients
        await self.init()

    async def init(self):
        _cl = []
        for i in range(len(self)):
            try:
                cl = self.clients[i]
                await cl.client.connect()
                _cl.append(cl)
                await self.clients[i].client.connect()
            except:
                c = await AccountModel.get(unique_id=self.clients[i].id)
                await c.delete()
        self.clients = _cl
    async def view_posts(self, name: str, account_id: str, posts: list[int]):
        client = self.get_client(account_id)
        try:
            await client(
                GetMessagesViewsRequest(
                    peer=name,
                    id=posts,
                    increment=True
                )
            )
        except Exception as ex:
            print(ex)
            print("view_error", client)

    async def get_last_post_id(self, channel_name: str) -> int:
        for _ in range(5):
            client = self.get_random_client()
            try:
                messages = client.iter_messages(channel_name)
                return (await anext(messages)).id
            except (SessionRevokedError, AuthKeyUnregisteredError) as ex:
                print("get_error: ", client)
                print(ex)
                # TODO если сессия отклонена удалить аккаунт с бд и залогировать
                continue
        return 0

    def get_random_client(self) -> TelegramClient:
        return random.choice(self.clients).client

    def get_client(self, account_id):
        for client in self.clients:
            if account_id == client.id:
                return client.client

    def get_active_account_ids(self) -> list[str]:
        ret = []
        for client in self.clients:
            ret.append(client.id)
        return ret

    def __len__(self) -> int:
        return len(self.clients)
