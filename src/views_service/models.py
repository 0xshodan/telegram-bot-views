from tortoise import Model, fields
import socks
import random


class Task(Model):
    body = fields.TextField()


class Channel(Model):
    name = fields.CharField(max_length=100)
    last_post_id = fields.IntField(default=0)
    task = fields.ForeignKeyField("models.Task", related_name="channels")

class Proxy(Model):
    ip = fields.CharField(max_length=15)
    port = fields.CharField(max_length=5)
    username = fields.CharField(max_length=100, null=True)
    password = fields.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return f"{self.ip}:{self.port}"

    def to_socks(self) -> tuple:
        _ret = [socks.HTTP, self.ip, int(self.port)]
        if self.username:
            _ret.append(True)
            _ret.append(self.username)
        if self.password:
            _ret.append(self.password)
        return tuple(_ret)

    @classmethod
    async def get_available(cls):
        proxies = await Proxy.all()
        return random.choice(proxies)


class Account(Model):
    unique_id = fields.UUIDField(pk=True)
    proxy = fields.ForeignKeyField("models.Proxy", related_name="accounts", null=True)
    session = fields.CharField(max_length=250, null=True)
    views = fields.IntField(default=0)
    tdata_path = fields.CharField(max_length=250, unique=True)
    unloaded = fields.BooleanField(default=True)

    def __str__(self):
        return self.id