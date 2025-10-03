from celery import Celery
from config.config import config
from celery.signals import task_postrun, task_failure

celery_app = Celery(
    "jc-microservices-app-1",
    backend=config.celery_backend_url,
    broker=config.celery_broker_url,
    include=["src.tasks"],
)

celery_app.conf.update(
    enable_utc=True,
    timezone="UTC",
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    task_track_started=True,  # Track when a task starts
    task_serializer="json",  # Use JSON for task serialization
    result_serializer="json",  # Use JSON for result serialization
    accept_content=["json"],  # Accept only JSON content
    worker_send_task_events=True,  # Send task events from the worker
    task_send_sent_event=True,  # Send an event when a task is sent
    task_ignore_result=False,  # Do not ignore task results
    worker_prefetch_multiplier=1,  # Prefetch only one task at a time
)


#signlas to trigger before or after an event.
@task_postrun.connect
def task_postrun_handler(
    sender=None, task_id=None, task=None, retval=None, state=None, *args, **kwargs
):
    pass



@task_failure.connect
def task_failure_handler(task_id=None, exception=None, *args, **kwargs):
    pass