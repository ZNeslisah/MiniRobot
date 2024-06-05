import usocket as socket
import network
import select
import utime
import asyncio
from . import *
from .logging import Logger

class PiNode:
    def __init__(self, wifi_ssid, wifi_password, port, logging = 'ERROR', timeout = None):
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.port = port
        self.self_socket = None
        self.master_socket = None
        self.ip_address = None
        self.logging = Logger('PiNode', logging)
        self.timeout = timeout

    def _connect_to_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.wifi_ssid, self.wifi_password)

        self.logging.debug('Connecting to Wi-Fi...')
        
        # Wait until the connection is established with polling
        start_time = utime.ticks_ms()
        while not wlan.isconnected():
            current_time = utime.ticks_ms()
            if current_time - start_time > CONN_TIMEOUT:
                self.logging.error("Wifi Connection timed out.")
                self.logging.error('Quitting.')                
                exit(-1)

        self.ip_address = wlan.ifconfig()[0]
        
        self.logging.debug(f'Connected to Wi-Fi at: {self.ip_address}')
        
        return self.ip_address

    def _init_node(self):
        self.self_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.self_socket.bind((self.ip_address, self.port))
        except OSError as err:
            self.logging.error(f'Could not bind to {(self.ip_address, self.port)}.')
            self.logging.error('Quitting.')
            exit(-1)

    def _connect_to_master(self):
        # Start listening for incoming connections
        self.self_socket.listen()

        self.logging.debug(f'Listening for incoming connections at {(self.ip_address, self.port)}')
        
        async def accept_connection():
            self.master_socket, master_address = await self.self_socket.accept()
            self.logging.debug(f'Connection from: {master_address}')
            self.master_socket.settimeout(self.timeout)

        task = asyncio.create_task(accept_connection())

        # Wait until the connection is established with polling        
        start_time = utime.ticks_ms()
        while not task.done():
            current_time = utime.ticks_ms()
            if current_time - start_time > CONN_TIMEOUT:
                self.logging.error("Master connection timed out.")
                self.logging.error('Quitting.')
                task.cancel()
                exit(-1)

    def set_timeout(self, delay=None):
        self.timeout = delay
        self.master_socket.settimeout(delay)

    def init(self):
        self._connect_to_wifi()
        self._init_node()
        self._connect_to_master()
        
    def make_poll(self):
        poller = select.poll()
        poller.register(self.master_socket, select.POLLIN)
        poller.register(self.master_socket, select.POLLOUT)
        return poller

    def receive(self):
        try:
            data = self.master_socket.recv(1024)
            if not data:
                return None
            self.logging.debug(f'Data received: {data}')
            return data.decode()
        except OSError as e:
            self.logging.error(f'Error while receiving data: {e}')
            return None
    
    def send(self, data):
        encoded = data.encode()
        try:
            self.master_socket.sendall(encoded)
            self.logging.debug('Data sent: ', encoded)
            return True
        except OSError as e:
            self.logging.error(f'Error while sending data: {e}')
            return False
            

    def end_connection(self):
        if self.master_socket:
            self.master_socket.close()
        if self.self_socket:
            self.self_socket.close()
        self.logging.debug('Connection closed.')

