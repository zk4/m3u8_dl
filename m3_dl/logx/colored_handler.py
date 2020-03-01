from logging import Handler
from termcolor import colored

# class color:
#     W  = '\033[0m'  # white (normal)
#     R  = '\033[31m' # red
#     G  = '\033[32m' # green
#     O  = '\033[33m' # orange
#     B  = '\033[34m' # blue
#     P  = '\033[35m' # purple
#     C  = '\033[36m' # cyan
#     GR = '\033[37m' # gray


class ColoredHandler(Handler):
    def emit(self, record):
        if record.levelname  == "INFO":
            record.msg=colored( record.getMessage(),'green')
        if record.levelname  == "ERROR":
            record.msg=colored(record.getMessage(),'cyan')
        if record.levelname  == "CRITICAL":
            record.msg=colored( record.getMessage(),'red')
        if record.levelname  == "WARNING":
            record.msg=colored( record.getMessage(),'blue')

