from celery import Celery
from app.config import REDIS_URL

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.imports = ("app.agents.tasks",)

celery_app.conf.task_routes = {
    "app.agents.tasks.*": {"queue": "celery"}
}