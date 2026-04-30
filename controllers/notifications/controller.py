from notifypy import Notify
import config
import os
icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', 'GUI', 'assets', 'logo.png'))
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
        notification.icon = icon_path
        notification.title = self.title
        notification.message = self.message
        notification.send()

