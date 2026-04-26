from notifypy import Notify
import config

class notif_controller():
    def __init__(self):
        self.title = None
        self.message = None

    def notify(self, title, message):
        if not config.OPTIONS['notifications']: return
        self.title = title
        self.message = message
        self.send_notif()

    def send_notif(self):

        notification = Notify()
        notification.title = self.title
        notification.message = self.message
        notification.send()

