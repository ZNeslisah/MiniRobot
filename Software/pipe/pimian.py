from mpi.pinode import PiNode

WIFI_SSID = "mechalab_intra"
WIFI_PASSWORD = "mechastudent"
PORT = 8080

if __name__ == '__main__':
    node = PiNode(WIFI_SSID, WIFI_PASSWORD, PORT)
    node.connectWifi()
    node.initNode()
    node.connect()
    while True:
        data = node.receive()
        if data:
            print(f"Received: {data}")
            node.send("ACK")
        else:
            print('Ended Connection.')
            break
    node.endConnection()
