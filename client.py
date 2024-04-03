import pickle
import socket
import ssl
import struct

import cv2

# Client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '127.0.1.1'
port = 10051

# Wrap the client socket with SSL/TLS
client_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
client_context.load_verify_locations("/home/fiend/Scripts/Web_surveilance/server.crt")
client_socket = client_context.wrap_socket(client_socket, server_hostname='Hrishikesh M Rao')

client_socket.connect((host_ip, port))


vid = cv2.VideoCapture(0)
while vid.isOpened():
    
    _, frame = vid.read()
    a = pickle.dumps(frame)
    message = struct.pack("Q", len(a)) + a
    client_socket.sendall(message)
    
    cv2.imshow("Sending...", frame)

    # Receive messages from the server
    try:
        # Attempt to receive data from the server
        data = client_socket.recv(1024)
        if data:
            # Decode and print the received message
            message = data.decode()
            print("Server says:", message)
            
    except socket.error as e:
        # Handle errors if any
        print("Error receiving data:", e)
        break

    key = cv2.waitKey(10) 
    if key == 13:
        break
    
client_socket.close()
cv2.destroyAllWindows()
