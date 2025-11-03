from .notifications import NotificationSender

class SendNotification:

    

    @classmethod
    def send(cls,notification:NotificationSender):
        notification.send()