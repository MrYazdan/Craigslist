import logging


# configure notifiers:
class NotifyHandler(logging.Handler):
    def emit(self, record):
        pass
        # notification.notify(
        #     title=f"🦎 Craigslist crawler",
        #     message=self.format(record),
        #     app_icon="lizard",
        #     timeout=10,
        # )
