import socket
import threading
from queue import Queue
import logging
import time
from . import *
from .package import Package

class Connection:
    def __init__(self, conn: socket.socket, addr: int) -> None:
        self.socket = conn
        self.addr = addr
        self.sendQueue = Queue(MAX_QUEUE_SIZE)
        self.recvQueue = Queue(MAX_QUEUE_SIZE)
        self.connected = threading.Event()
        self.connected.set()
        self.threadRecv = None
        self.threadSend = None

class Pipe:
    def __init__(self) -> None:
        self.connections = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def listen(self):
        raise NotImplementedError('Listen function must be implemented.')

    def close(self):
        for conn in self.connections:
            conn.connected.clear()

    def available(self, idx: int) -> bool:
        if idx > len(self.connections) - 1:
            return False
        if not self.connections[idx].connected.is_set():
            return False
        return True

    def numOfConnections(self) -> int:
        return len(self.connections)

    def send(self, idx: int, pkg: Package):
        self.connections[idx].sendQueue.put(pkg)

    def receivable(self, idx) -> bool:
        return self.connections[idx].recvQueue.qsize() > 0

    def getLastRecv(self, idx) -> Package:
        pkg = None
        while not self.connections[idx].recvQueue.empty():
            pkg = self.connections[idx].recvQueue.get()
        return pkg

    def handleRecv(self, conn: Connection):
        socket, addr = conn.socket, conn.addr
        logging.info(f"[PIPE] New sender : {addr} connected.")
        
        while conn.connected.is_set():
            try:
                byteArray = socket.recv(HEADER)
            except ConnectionResetError as err:
                logging.warning(f'[PIPE] Connection reset by peer.')
                conn.connected.clear()
                break
            except RuntimeError as err:
                logging.warning(f'[PIPE] Unkown error : {err}.')
                conn.connected.clear()
                break
            
            logging.info(f"[PIPE] Received from {addr} : {byteArray}")

            pkg: Package = Package.decode(byteArray, addr[1])
            
            if not pkg:
                logging.info(f"[PIPE] Received NULL Package : {addr}.")
                conn.connected.clear()
                break
            
            conn.recvQueue.put(pkg)

        socket.close()
        self.connections.remove(conn)
        logging.info(f"[PIPE] Closed receiver connection : {addr}.")

    def handleSend(self, conn: Connection):
        socket, addr = conn.socket, conn.addr
        logging.info(f"[PIPE] New receiver : {addr} connected.")
        
        while conn.connected.is_set():
            # SENDING
            if conn.sendQueue.empty():
                continue

            pkg: Package = conn.sendQueue.get()
            
            totalsent = 0
            msglen = len(pkg.encoded)
            while totalsent < msglen:
                try:
                    sent = socket.send(pkg.encoded[totalsent:])
                except OSError as err:
                    logging.error(f'[PIPE] OS Error: {err.strerror}.')
                    conn.connected.clear()
                    break
                if not sent:
                    logging.warning('[BROKEN PIPE] Socket connection broken.')
                    conn.connected.clear()
                    break
                
                totalsent = totalsent + sent

            if totalsent == msglen:
                logging.info(f"[PIPE] Sent to {addr}: {pkg.encoded}.")
        
        socket.close()
        logging.info(f"[PIPE] Closed sender connection : {addr}.")


class BindingPipe(Pipe):
    def __init__(self, maxConnection, timeOut) -> None:
        self.maxConnection = maxConnection
        self.timeOut = timeOut
        super().__init__()
        try:
            self.socket.bind(SERVER_ADDR)
        except OSError as err:
            logging.error(f'[PIPE] OS Error: {err.strerror}.')
            logging.error('[PIPE] Quitting.')
            exit(-1)
    
    def listen(self):
        if len(self.connections) >= self.maxConnection:
            return
        self.socket.listen()
        logging.info(f"[PIPE] Listening on {HOST}")
        
        startTime = time.time()
            
        while len(self.connections) < self.maxConnection:
            # Below function blocks the code untill a new connection is made
            conn, addr = self.socket.accept()
            
            newConn = Connection(conn, addr)

            newConn.threadRecv = threading.Thread(target=self.handleRecv, args=(newConn,))
            newConn.threadSend = threading.Thread(target=self.handleSend, args=(newConn,))
            newConn.threadRecv.start()
            newConn.threadSend.start()
            self.connections.append(newConn)

            logging.info(f"[PIPE] Active Connections : {len(self.connections)}")
            
            if self.timeOut and time.time() - startTime > self.timeOut:
                logging.warning(f"[PIPE] Pipe listen timed out.")
        return

class ConnectingPipe(Pipe):
    def __init__(self) -> None:
        super().__init__()

    def listen(self, addrList):
        # Officially connecting to the server.
        for addr_ in addrList:
            
            try:
                self.socket.connect(addr_)
            except ConnectionRefusedError as err:
                logging.error(f'[PIPE] Connection refused.')
                logging.error('[PIPE] Quitting.')
                exit(-1)
            
            logging.info(f"[PIPE] Connected to {HOST}.")

            conn = self.socket
            addr = self.socket.getsockname()
            newConn = Connection(conn, addr)

            newConn.threadRecv = threading.Thread(target=self.handleRecv, args=(newConn,))
            newConn.threadSend = threading.Thread(target=self.handleSend, args=(newConn,))
            newConn.threadRecv.start()
            newConn.threadSend.start()

            self.connections.append(newConn)

            logging.info(f"[PIPE] Active Connections : {len(self.connections)}")
        