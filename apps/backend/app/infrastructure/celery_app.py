from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery("analise", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.broker_connection_retry_on_startup = True

# O comando `celery -A app.infrastructure.celery_app` procura por `app` no módulo.
app = celery_app
