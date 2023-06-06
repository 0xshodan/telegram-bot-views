from celery import Celery
from tortoise import Tortoise, run_async
from celery.signals import celeryd_init


async def init_db():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['src.admin.models', 'src.views_service.models']}
    )
    await Tortoise.generate_schemas()


@celeryd_init.connect
def init_celery(**kwargs):
    run_async(init_db())

celery_app = Celery("views", broker="redis://localhost:6379")
celery_app.conf.beat_schedule = {
    'check-channels': {
        'task': 'src.views_service.tasks.check_new_posts',
        'schedule': 60.0,
    },
}

