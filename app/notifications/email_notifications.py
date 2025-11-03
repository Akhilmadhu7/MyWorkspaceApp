from .notifications import NotificationSender
from typing import Optional
import smtplib, enum
from logger import logger
from config.config import config




class EmailNotification(NotificationSender):

    SMTP_TYPE = 'smtp.gmail.com'

    def __init__(self, to_address:str, message:str, subject:Optional[str] = None):
        self.to_address = to_address
        self.message = message
        self.subject = subject

    
    def send(self):
        logger.info(f"Email Notification is being called....")
        try:
            with smtplib.SMTP(self.SMTP_TYPE) as connection:
                connection.starttls()
                connection.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
                connection.sendmail(
                    config.EMAIL_USERNAME,
                    self.to_address,
                    msg=f"{self.subject}\n\n{self.message}"
                )
        except Exception as error:
            logger.error(f"error sending notification is: {error}.")
            raise error


        