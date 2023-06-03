from redis.asyncio.client import Redis
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from src.admin.models import Admin
import os
from tortoise.contrib.fastapi import register_tortoise
from starlette.responses import RedirectResponse, Response
from src.views_service.tasks import view_channel


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

@app.get("/")
async def index():
    return RedirectResponse(url="/admin")

@app.get("/api/views")
async def api_views(name: str, count: int, time: int):
    view_channel.delay(name, count, time)
    return Response()


@app.on_event("startup")
async def startup():
    r = Redis(
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

app.mount("/admin", admin_app)

register_tortoise(
    app,
    config={
        "connections": {"default": "sqlite://db.sqlite3"},
        "apps": {
            "models": {
                "models": ["src.admin.models", "src.views_service.models"],
                "default_connection": "default",
            }
        },
    },
    generate_schemas=True,
)

