import os

from celery import Celery
from celery.schedules import crontab

from settings.conf import ENV_ID

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'settings.env.{ENV_ID}')

app = Celery('uldar_net')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-sessions-daily': {
        'task': 'apps.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=3, minute=0),
    },
    'cleanup-old-notifications-weekly': {
        'task': 'apps.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=4, minute=0, day_of_week='monday'),  # every Monday at 04:00
    },

}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()



