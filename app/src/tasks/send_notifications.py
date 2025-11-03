from notifications import EmailNotification
from celery import shared_task
from .base_tasks import NotificationTask
from logger import logger
from config.celery import celery_app
from notifications import SendNotification, EmailNotification


# @celery_app.task(base=NotificationTask)
@shared_task(base=NotificationTask)
def send_notification(reciever_email:str, message:str, subject:str):
    logger.info(
        f"sending email. reciever: {reciever_email}, message: {message}, subject: {subject}"
    )
    e = EmailNotification(
        reciever_email ,message, subject
    )
    SendNotification.send(e)
    