from celery import Task
from logger import logger

class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    max_retries = 5
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = False

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(f'Task {task_id} succeeded with result: {retval}')
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        logger.error(f'Task {task_id} failed: {exc}')
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger.warning(f'Task {task_id} retrying: {exc}')
    
    def before_start(self, task_id, args, kwargs):
        """Called before task starts"""
        logger.info(f'Task {task_id} starting with args: {args}')


class NotificationTask(BaseTaskWithRetry):

    autoretry_for = (Exception, )
    max_retries = 3
    retry_backoff = True
    retry_backoff_max = 500
    retry_jitter=False