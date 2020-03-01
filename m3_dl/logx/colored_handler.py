from logging import Handler

class color:
    W  = '\033[0m'  # white (normal)
    R  = '\033[31m' # red
    G  = '\033[32m' # green
    O  = '\033[33m' # orange
    B  = '\033[34m' # blue
    P  = '\033[35m' # purple
    C  = '\033[36m' # cyan
    GR = '\033[37m' # gray


class ColoredHandler(Handler):
    def emit(self, record):
        if record.levelname  == "INFO":
            record.msg=color.G + record.getMessage()+ color.W
        if record.levelname  == "ERROR":
            record.msg=color.O + record.getMessage()+ color.W
        if record.levelname  == "CRITICAL":
            record.msg=color.R + record.getMessage()+ color.W
        if record.levelname  == "WARNING":
            record.msg=color.B + record.getMessage()+ color.W

