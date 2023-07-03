from src.admin.models import Admin
import bcrypt
from loguru import logger
from tortoise.exceptions import DoesNotExist


async def create_admin(username: str, password: str):
    try:
        await Admin.get(username=username)
    except DoesNotExist:
        bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(bytes, salt).decode("utf-8")
        await Admin.create(username=username, password=password_hash)
        logger.info(f"Created admin account with username: {username}")
