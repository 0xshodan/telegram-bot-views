from tortoise import Model, fields
import socks
import random

class Proxy(Model):
    ip = fields.CharField(max_length=15)
    port = fields.CharField(max_length=5)
    username = fields.CharField(max_length=100, null=True)
    password = fields.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return f"{self.ip}:{self.port}"

    def to_socks(self) -> tuple:
        _ret = [socks.HTTP, self.ip, self.port]
        if self.username:
            _ret.append(self.username)
        if self.password:
            _ret.append(self.password)
        return tuple(_ret)

    def get_available(self):
        proxies = Proxy.filter(client=None)
        return random.choice(proxies)




class Client(Model):
    unique_id = fields.UUIDField(pk=True)
    proxy = fields.OneToOneField("models.Proxy", related_name="client")
    session = fields.TextField(unique=True)

class Account(Model):
    views = fields.IntField()
    client = fields.ForeignKeyField("models.Client", related_name="accounts")
    tdata_path = fields.TextField(unique=True)
    unloaded = fields.BooleanField(default=True)

    def __str__(self):
        return self.id