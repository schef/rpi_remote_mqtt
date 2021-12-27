import sys
import logging.handlers

class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    green = "\033[92m"
    reset = '\x1b[0m'

    def make_fmt(self, color, level):
        return "[%(asctime)s.%(msecs)03d] [" + color + level + self.reset + "] %(message)s"

    def create_formatters(self):
        date_fmt = "%d.%m %H:%M:%S"

        self.formatters = {
            logging.DEBUG: logging.Formatter(self.make_fmt(self.blue, "DBG"), datefmt=date_fmt),
            logging.INFO: logging.Formatter(self.make_fmt(self.green, "INF"), datefmt=date_fmt),
            logging.WARNING: logging.Formatter(self.make_fmt(self.yellow, "WRN"), datefmt=date_fmt),
            logging.ERROR: logging.Formatter(self.make_fmt(self.red, "ERR"), datefmt=date_fmt),
            logging.CRITICAL: logging.Formatter(self.make_fmt(self.bold_red, "CRT"), datefmt=date_fmt)
        }

    def __init__(self):
        super().__init__()
        self.create_formatters()

    def format(self, record):
        return self.formatters.get(record.levelno).format(record)


def setup_custom_logger(name):
    logger = logging.getLogger(name)
    consoleHandler = logging.StreamHandler(sys.stdout)
    logFormatter = CustomFormatter()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)
    return logger

_logger = None
def get():
    global _logger
    if _logger is None:
        _logger = setup_custom_logger('root')
    return _logger
