from celery import Celery
from dotenv import load_dotenv
import os
from celery.utils.log import get_logger

logger= get_logger(__name__)

load_dotenv(".env")

celery_app = Celery("views", broker=os.environ.get("CELERY_BROKER_URL"))
celery_app.conf.beat_schedule = {
    'check-channels': {
        'task': 'src.views_service.tasks.check_new_posts',
        'schedule': 60.0,
    },
}

