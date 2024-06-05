from mpi.pinode import PiNode
import random
import utime

WIFI_SSID = "mechalab_intra"
WIFI_PASSWORD = "mechastudent"
PORT = 8080

if __name__ == '__main__':
    node = PiNode(WIFI_SSID, WIFI_PASSWORD, PORT)
    node.init()
    while True:
        # Generate random data
        data = random.randint(0, 100)
        utime.sleep(100)
        # Send data
        node.send(str(data))


