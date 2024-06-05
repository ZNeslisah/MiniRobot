class Logger:
    _DEBUG = 0
    _INFO = 1
    _WARNING = 2
    _ERROR = 3

    def __init__(self, name, loglevel) -> None:
        self.name = name
        if loglevel not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            raise ValueError('Invalid log level')

        if loglevel == 'DEBUG':
            self.loglevel = Logger._DEBUG
        elif loglevel == 'INFO':
            self.loglevel = Logger._INFO
        elif loglevel == 'WARNING':
            self.loglevel = Logger._WARNING
        elif loglevel == 'ERROR':
            self.loglevel = Logger._ERROR

    def debug(self, msg):
        if self.loglevel <= Logger._DEBUG:
            print(f'[{self.name}] {msg}')
    
    def info(self, msg):
        if self.loglevel <= Logger._INFO:
            print(f'[{self.name}] {msg}')
    
    def error(self, msg):
        print(f'[{self.name}] {msg}')

    def warning(self, msg):
        if self.loglevel <= Logger._WARNING:
            print(f'[{self.name}] {msg}')