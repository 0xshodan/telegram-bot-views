from redis.asyncio.client import Redis
from fastapi import FastAPI, Request
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from src.admin.models import Admin
import os
from tortoise.contrib.fastapi import register_tortoise
from starlette.responses import RedirectResponse, Response, JSONResponse
from src.views_service.accounts_manager import AccountsManager
from dotenv import load_dotenv
from src.views_service.models import Channel

load_dotenv(".env")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class CustomFastAPI(FastAPI):
    def setup_manager(self, manager):
        self.manager = manager

    @property
    def accounts_manager(self):
        return self.manager

app = CustomFastAPI()

@app.get("/")
async def index():
    return RedirectResponse(url="/admin")


@app.post("/api/viewPosts")
async def view_posts(request: Request):
    req_json = await request.json()
    print(req_json)
    await app.manager.view_posts(req_json["name"], req_json["account_id"], req_json["posts"])
    return Response()

@app.get("/api/getAccounts")
async def get_accounts():
    return JSONResponse({"accounts":app.manager.get_active_account_ids()})

@app.get("/api/getChannels")
async def get_channels():
    channels = await Channel.all().select_related("task")
    ret = []
    for channel in channels:
        ret.append(
            {
                "name":channel.name,
                "last_post_id":channel.last_post_id,
                "task":
                    {
                    "name":channel.task.name,
                    "body": channel.task.body
                    }
             }
             )
    return JSONResponse({"channels":ret})

@app.get("/api/getLastPost")
async def get_last_post(name:str):
    return JSONResponse({"id": await app.manager.get_last_post_id(name)})

app.mount("/admin", admin_app)

db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]
register_tortoise(
    app,
    config={
        "connections": {"default": f"asyncpg://{db_user}:{db_password}@db:5432/{db_name}"},
        "apps": {
            "models": {
                "models": ["src.admin.models", "src.views_service.models"],
                "default_connection": "default",
            }
        },
    },
    generate_schemas=True,
)
@app.on_event("startup")
async def startup():
    r = Redis(
        host="redis",
        decode_responses=True,
        encoding="utf8",
    )
    await admin_app.configure(
        logo_url="https://preview.tabler.io/static/logo-white.svg",
        template_folders=[os.path.join(BASE_DIR, "templates")],
        favicon_url="https://raw.githubusercontent.com/fastapi-admin/fastapi-admin/dev/images/favicon.png",
        providers=[
            UsernamePasswordProvider(
                login_logo_url="https://preview.tabler.io/static/logo.svg",
                admin_model=Admin,
            )
        ],
        redis=r,
    )
    manager = await AccountsManager.create()
    await manager.init()
    app.setup_manager(manager)
