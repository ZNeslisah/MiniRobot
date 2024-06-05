import socket

# Socket code to communicate with pinode
# Define the pinode IP address and port number
pinode_ip = '192.168.1.100'
pinode_port = 8080

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the pinode
sock.connect((pinode_ip, pinode_port))

# Send data to the pinode
data = "Hello, pinode!"
sock.sendall(data.encode())

# Close the socket
sock.close()
