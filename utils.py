class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Mailbox:
    debugLevel = 0

    @classmethod
    def debug(cls, msg):
        if cls.debugLevel > 0:
            print(f"{Bcolors.BOLD}{Bcolors.OKBLUE}[DEBUG] {msg}{Bcolors.ENDC}")

    @classmethod
    def warning(cls, msg):
        print(f"{Bcolors.BOLD}{Bcolors.FAIL}[WARN] {msg}{Bcolors.ENDC}")

    @classmethod
    def info(cls, msg):
        print(f"{Bcolors.BOLD}{Bcolors.WARNING}[INFO] {msg}{Bcolors.ENDC}")