from fastapi_admin.app import app
from fastapi_admin.resources import Link, Model, ToolbarAction, Field
from fastapi_admin.widgets import inputs
from fastapi_admin.file_upload import FileUpload
import os
from starlette.datastructures import FormData

from tortoise.queryset import QuerySet
from src.views_service.models import Proxy, Account, Channel, Task

from starlette.requests import Request

from fastapi_admin.enums import Method
from fastapi_admin.i18n import _
from src.admin.owner_resource import OwnerResource

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload = FileUpload(uploads_dir=os.path.join(BASE_DIR, "static", "uploads"))


@app.register
class Home(Link):
    label = "Home"
    icon = "fas fa-home"
    url = "/admin"


@app.register
class ProxyResource(Model):
    label = "Прокси"
    model = Proxy
    page_title = "Прокси"
    fields = [
        "id",
        "ip",
        "port",
        "username",
        "password",
    ]

    async def get_toolbar_actions(self, request: Request) -> list[ToolbarAction]:
        return [
            ToolbarAction(
                label=_("create"),
                icon="fas fa-plus",
                name="create",
                method=Method.GET,
                ajax=False,
                class_="btn-dark",
            ),
            ToolbarAction(
                label=_("import"),
                icon="fas fa-plus",
                name="import",
                method=Method.GET,
                ajax=False,
                class_="btn-success",
            ),
        ]


@app.register
class AccountResource(Model):
    label = "Аккаунты"
    model = Account
    page_title = "Аккаунты"
    fields = [
        "unique_id",
        "proxy",
        "session",
    ]

    async def get_toolbar_actions(self, request: Request) -> list[ToolbarAction]:
        return [
            ToolbarAction(
                label=_("create"),
                icon="fas fa-plus",
                name="create",
                method=Method.GET,
                ajax=False,
                class_="btn-dark",
            ),
            ToolbarAction(
                label=_("import"),
                icon="fas fa-plus",
                name="import",
                method=Method.GET,
                ajax=False,
                class_="btn-success",
            ),
        ]


@app.register
class ChannelResource(OwnerResource):
    label = "Каналы"
    model = Channel
    page_title = "Отслеживаемые каналы"
    fields = ["name", "last_post_id", Field("task", input_=inputs.ForeignKey(Task))]


@app.register
class TaskResource(OwnerResource):
    label = "Задачи"
    model = Task
    page_title = "Задачи"
    fields = [
        "name",
        "body",
        "channels",
    ]
