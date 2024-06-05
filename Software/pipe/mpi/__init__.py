import socket
# from types import SimpleNamespace

# TCP/IP Settings
HEADER = 64
SERVER_PORT = 5050
HOST = '192.168.1.122' # socket.gethostbyname(socket.gethostname())
SERVER_ADDR = (HOST, SERVER_PORT)
MAX_QUEUE_SIZE = 2

# PACKAGE Settings
FORMAT = 'UTF-8'
# PACKAGE_T = SimpleNamespace(
#     GAME_TICK = 'GAMET',
#     USER_UPDATE = 'USERU',
#     DISCONNECT = 'DISCO',
#     ERROR = 'ERROR',
#     DEBUG = 'DEBUG'
# )
DELIM = '%'
EOP = '!'