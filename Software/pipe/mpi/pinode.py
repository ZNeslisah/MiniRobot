import usocket as socket
import network
import select
import utime

class PiNode:
    def __init__(self, wifi_ssid, wifi_password, port, debug=False, timeout = None):
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.port = port
        self.self_socket = None
        self.master_socket = None
        self.ip_address = None
        self.debug = debug
        self.timeout = timeout

    def connectWifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.wifi_ssid, self.wifi_password)

        if self.debug:
            print('[PiNode] Connecting to Wi-Fi...')
        # Wait until the connection is established with polling
        start_time = utime.ticks_ms()
        while not wlan.isconnected():
            current_time = utime.ticks_ms()
            if current_time - start_time > self.timeout:
                print("[PiNode] Connection timed out.")
                print('[PiNode] Quitting.')                
                exit(-1)

        self.ip_address = wlan.ifconfig()[0]
        if self.debug:
            print('[PiNode] Connected to Wi-Fi at: ', self.ip_address)
        return self.ip_address

    def initNode(self):
        self.self_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.self_socket.bind((self.ip_address, self.port))
        except OSError as err:
            print(f'[PiNode] Could not bind to {(self.ip_address, self.port)}.')
            print('[PiNode] Quitting.')
            exit(-1)


    def connect(self):
        # Start listening for incoming connections
        self.self_socket.listen()
        
        if self.debug:
            print(f"[PiNode] Waiting for a client to connect at {(self.ip_address, self.port)}")
        
        # Wait for a client to connect
        self.master_socket, master_address = self.self_socket.accept()
        
        if self.debug:
            print('[PiNode] Connection from: ', master_address)

    def setTimeout(self, delay=None):
        self.master_socket.settimeout(delay)
        
    def makeRecievePoll(self):
        poller = select.poll()
        poller.register(self.master_socket, select.POLLIN)
        return poller

    def makeSendPoll(self):
        poller = select.poll()
        poller.register(self.master_socket, select.POLLOUT)
        return poller

    def receive(self):
        try:
            data = self.master_socket.recv(1024)
            if data:
                return data.decode()
            else:
                # Connection maybe closed by the master
                return None
        except OSError as e:
            # Check for EWOULDBLOCK or timeout, meaning no data yet
            if e.args[0] in [11, 110]:
                return None
            else:
                raise
        finally:
            # Reset the timeout to None to disable it
            self.master_socket.settimeout(None)
    
    def send(self, data):
        try:
            self.master_socket.sendall(data.encode())
            print("Data sent:", data)
        except OSError as e:
            print("Error while sending data:", e)
            

    def endConnection(self):
        if self.master_socket:
            self.master_socket.close()
        if self.self_socket:
            self.self_socket.close()
        if self.debug:
            print("[PiNode] Connection closed.")

