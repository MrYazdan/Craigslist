import logging
from plyer import notification


# configure notifiers:
class NotifyHandler(logging.Handler):
    def emit(self, record):
        notification.notify(
            title=f"🦎 Craigslist crawler",
            message=self.format(record),
            app_icon="lizard",
            timeout=10,
        )