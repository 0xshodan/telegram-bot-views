import os
from opentele.td import TDesktop, Account
from opentele.api import UseCurrentSession
from dataclasses import dataclass

@dataclass
class TelegramAccount:
    account: Account
    views: int = 0


class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class AccountsManager(metaclass=SingletonMeta):

    @classmethod
    async def create(cls, accounts_path: str, sessions_path: str):
        self = AccountsManager()
        self.accounts_path = accounts_path
        self.sessions_path = sessions_path
        try:
            if self.accounts == []:
                self.accounts = await self.load_accounts()
        except AttributeError:
            self.accounts = await self.load_accounts()
        return self

    async def load_accounts(self) -> list[TelegramAccount]:
        accounts: list[TelegramAccount] = []
        try:
            account_dirs = next(os.walk(self.accounts_path))[1]
        except StopIteration:
            raise FileNotFoundError
        for account_dir in account_dirs:
            tdata_folder = os.path.abspath(f"{self.accounts_path}/{account_dir}/tdata")
            tdesk = TDesktop(tdata_folder)
            client = await tdesk.ToTelethon(
                session=f"{self.sessions_path}/ssid{account_dir}.session",
                flag=UseCurrentSession
                )
            accounts.append(TelegramAccount(client))
        return accounts

    async def init(self):
        for i in range(len(self)):
            await self.accounts[i].account.connect()

    def __len__(self) -> int:
        return len(self.accounts)
