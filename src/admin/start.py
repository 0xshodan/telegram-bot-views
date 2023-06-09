from redis.asyncio.client import Redis
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from src.admin.models import Admin
import os
from tortoise.contrib.fastapi import register_tortoise
from src.views_service.accounts_manager import AccountsManager
from dotenv import load_dotenv
from src.admin.api import app
from src.admin.create_admin import create_admin

load_dotenv(".env")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


app.mount("/admin", admin_app)

db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]
default_admin_username = os.environ["DEFAULT_ADMIN_USERNAME"]
default_admin_password = os.environ["DEFAULT_ADMIN_PASSWORD"]
register_tortoise(
    app,
    config={
        "connections": {
            "default": f"asyncpg://{db_user}:{db_password}@db:5432/{db_name}"
        },
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
    await create_admin(default_admin_username, default_admin_password)
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
