from celery import Celery, Task
from config.config import config
from celery.signals import task_postrun, task_failure
from kombu import Queue, Exchange
from logger import logger

_celery_app = None

def get_celery_app():
    global _celery_app
    if _celery_app is None:
        _celery_app = Celery(
            "slack-clone",
            backend=config.celery_backend_url,
            broker=config.celery_broker_url,
            include=["src.tasks"],
        )
        
        _celery_app.conf.update(
            enable_utc=True,
            timezone="UTC",
            broker_connection_retry=True,
            broker_connection_retry_on_startup=True,
            task_track_started=True,
            task_serializer="json",
            result_serializer="json",
            accept_content=["json"],
            worker_send_task_events=True,
            task_send_sent_event=True,
            task_ignore_result=False,
            worker_prefetch_multiplier=1,
        )
        
        _celery_app.conf.task_queues = (
            Queue("notification_queue", 
                  Exchange('notification_exchange', type='direct'), 
                  routing_key='notification_key'),
        )
        
        _celery_app.conf.task_routes = {
            'src.tasks.send_notifications.send_notification': {
                'queue': 'notification_queue',
                'routing_key': 'notification_key'
            }
        }
    
    return _celery_app

# For worker command line
celery_app = get_celery_app()


#signlas to trigger before or after an event.
@task_postrun.connect
def task_postrun_handler(
    sender=None, task_id=None, task=None, retval=None, state=None, *args, **kwargs
):
    print("-"*20)
    logger.info(
        f"post run connect sender: {sender}, task: {task}, state: {state}"
    )



@task_failure.connect
def task_failure_handler(task_id=None, exception=None, *args, **kwargs):
    logger.info(
        f"post run connect exception: {exception}"
    )