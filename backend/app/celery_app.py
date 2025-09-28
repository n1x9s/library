"""
Конфигурация Celery для фоновых задач
"""

from celery import Celery
from app.core.config import settings

# Создание экземпляра Celery
celery_app = Celery(
    "library_exchange",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"],
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Настройка расписания задач
celery_app.conf.beat_schedule = {
    "send-return-reminders": {
        "task": "app.tasks.send_return_reminders",
        "schedule": 24 * 60 * 60,  # Каждые 24 часа
    },
    "cleanup-old-notifications": {
        "task": "app.tasks.cleanup_old_notifications",
        "schedule": 7 * 24 * 60 * 60,  # Каждую неделю
    },
}

if __name__ == "__main__":
    celery_app.start()
