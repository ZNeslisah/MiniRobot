from machine import Pin
import utime
from server import *

WIFI_SSID = "mechalab_intra"
WIFI_PASSWORD = "mechastudent"
PORT = 8080


server = MyMicroServer(WIFI_SSID, WIFI_PASSWORD, PORT)
IP_ADDRESS = server.connect_to_wifi()
server.setup_server(IP_ADDRESS)
conn = server.wait_for_connection()


led = Pin(6, Pin.OUT)


while True:
    received = server.receive_data()
    if received:
        received = received.split('*')
        if received[0] == "wait":
            led.value(0)
            continue
        else:
            print(f"Shoot with {received[1]}")
            time.sleep(10)
            print(f"I am performing {received[2]}")
            time.sleep(0.5)
            print(f"I am performing {received[3]}")
            time.sleep(3)
            print(f"I am performing {received[4]}")
            led.value(1)
        
        
    