import socket


# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Define the IP address and port of the pinode
pinode_ip = '192.168.1.100'
pinode_port = 8080
# Connect to the pinode
sock.connect((pinode_ip, pinode_port))

while True:
    try:
        # Receive data from the pinode
        data = sock.recv(512)
        # Process the received data
        split = data.decode().splitlines()
        print(f'Numer of data: {len(split)}')
        for s in split:
            print("Received data: ", s)
    except Exception as e:
        print("An error occurred:", str(e))

