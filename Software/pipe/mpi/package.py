import logging
from . import (
    PACKAGE_T, EOP, DELIM, FORMAT
)
# Socket Data Handler

class Package:

    def __init__(self, message: str, port: int, type: str = PACKAGE_T.ERROR) -> None:
        self.port: int = port
        self.type = type
        self.message = message
        self.encoded = (type + DELIM + message + EOP).encode(FORMAT)
        self.data = None

    def valid(self):
        if self.message == '':
            return False
        # Hard codded port validity check.
        if self.port < 1024 or self.port > 65536:
            return False
        if self.data == None:
            return False
        # if self.type not in PACKAGE_T.__dict__:
        #     return False
        return True

    @staticmethod
    def decode(encoded: bytearray, port):
        message = encoded.decode(FORMAT)
        
        if not message:
            logging.warning(f'[PACKAGE] Null Package.')
            return None
        
        lasEOP = message.rfind(EOP)

        if lasEOP == -1:
            logging.warning(f'[PACKAGE] Incomplete Package: "{message}".')
            # Create an error package and return that
            return Package(message, port, type=PACKAGE_T.ERROR)
        
        prevLastEOP = message.rfind(EOP, 0, lasEOP)
        if prevLastEOP == -1:
            message = message[:lasEOP+1]
        message = message[prevLastEOP+1:lasEOP+1]
        
        tokens = message[:-1].split(DELIM)
        packageType = tokens[0]

        # Create Package
        package = Package(
            ''.join(tokens[1:]), port, type=packageType)

        if packageType == PACKAGE_T.GAME_TICK:
            package.data = Package.decodeGameTick(tokens[1:])
        elif packageType == PACKAGE_T.USER_UPDATE:
            package.data = Package.decodeUserUpdate(tokens[1:])
        elif packageType == PACKAGE_T.DISCONNECT:
            package.data = Package.decodeMessage(tokens[1:])
        elif packageType == PACKAGE_T.ERROR:
            package.data = Package.decodeMessage(tokens[1:])
        elif packageType == PACKAGE_T.DEBUG:
            package.data = Package.decodeMessage(tokens[1:])
        else:
            logging.warning(f'[PACKAGE] Unknown Package Type: "{packageType}".')
            package.type = PACKAGE_T.ERROR
        
        if not package.valid():
            logging.warning(f'[PACKAGE] Invalid Package: "{message}".')
            package.type = PACKAGE_T.ERROR

        return package

    @staticmethod
    def encode(data, type, port):
        # Empty Package
        package = Package('', port)

        if type == PACKAGE_T.GAME_TICK:
            package = Package.encodeGameTick(data, port)
        elif type == PACKAGE_T.USER_UPDATE:
            package = Package.encodeUserUpdate(data, port)
        elif type == PACKAGE_T.DISCONNECT:
            package = Package.encodeMessage(data, port, type)
        elif type == PACKAGE_T.ERROR:
            package = Package.encodeMessage(data, port, type)
        elif type == PACKAGE_T.DEBUG:
            package = Package.encodeMessage(data, port, type)
        else:
            raise ValueError(f' Unknown Package Type: "{type}".')
        
        package.data = data
        if not package.valid():
            raise ValueError(f'Invalid Package from: "{data}".')
        return package

    @staticmethod
    def decodeGameTick(tokens):
        if len(tokens) != 6: # num of data points 2 * 3
            logging.warning(f'[PACKAGE] Invalid Syntax: "{"%".join(tokens)}".')
            return None
        # BALL % P1 % P2
        data = dict()

        data['ball'] = [float(tokens[0]), float(tokens[1])]
        data['ply1'] = [float(tokens[2]), float(tokens[3])]
        data['ply2'] = [float(tokens[4]), float(tokens[5])]
        
        return data

    @staticmethod
    def encodeGameTick(pList, port):
        # BALL % P1 % P2
        message = ''
        message += ''.join([str(p) + '%' for p in pList[:-1]])
        message += str(pList[-1])

        pkg = Package(message, port, type = PACKAGE_T.GAME_TICK)
        
        return pkg

    @staticmethod
    def decodeUserUpdate(tokens):
        if len(tokens) != 1:
            return None
        return float(tokens[0])

    def encodeUserUpdate(yFrac, port):
        message = str(yFrac)
        return Package(message, port, type = PACKAGE_T.USER_UPDATE)

    @staticmethod
    def decodeMessage(tokens):
        msg = ''.join(tokens)
        return msg
    
    @staticmethod
    def encodeMessage(message, port, type):
        return Package(message, port, type)
