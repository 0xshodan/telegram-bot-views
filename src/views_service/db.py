from tortoise import Tortoise, run_async
from dotenv import load_dotenv
import os
from celery.utils.log import get_logger

logger= get_logger(__name__)

load_dotenv(".env")
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]

async def init_db():
    await Tortoise.init(
        db_url=f"psycopg://{db_user}:{db_password}@db:5432/{db_name}",
        modules={'models': ['src.admin.models', 'src.views_service.models']}
    )
    logger.info("db_started")
    await Tortoise.generate_schemas()

run_async(init_db())