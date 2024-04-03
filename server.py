import pickle
import socket
import ssl
import struct

import cv2


# Function to check if eyes are closed
def check_eyes_closed(gray_frame):
    eye_cascade = cv2.CascadeClassifier('/home/fiend/Scripts/Web_surveilance/haarcascade_eye.xml')
    eyes = eye_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(eyes) == 0

def extract_frame(data):
    while len(data) < payload_size:
        packet = client_socket.recv(4*1024)
        if not packet:
            break
        data += packet

    if len(data) < payload_size:
        return 0

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4*1024)

    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    
    return frame

# Server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
print('HOST NAME:', host_name)
host_ip = socket.gethostbyname(host_name)
print('HOST IP:', host_ip)
port = 10051
socket_address = (host_ip, port)

# Wrap the server socket with SSL/TLS
server_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
server_context.load_cert_chain(certfile="/home/fiend/Scripts/Web_surveilance/server.crt", keyfile="/home/fiend/Scripts/Web_surveilance/server.key")
server_socket = server_context.wrap_socket(server_socket, server_side=True)

server_socket.bind(socket_address)
server_socket.listen(5)
print('Socket now listening')

client_socket = 0

while not client_socket:
    client_socket, addr = server_socket.accept()
    
print('Connection from:', addr)
    
data = b""
payload_size = struct.calcsize("Q")

while True:
    
    frame = extract_frame(data)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if check_eyes_closed(gray_frame):
        message = "Eyes closed"
        client_socket.sendall(struct.pack("Q", len(message)) + message.encode())
    else:
        message = "Eyes open"
        client_socket.sendall(struct.pack("Q", len(message)) + message.encode())

    cv2.imshow('Receiving...', frame)
    
    key = cv2.waitKey(10)
    if key == 13:
        break

client_socket.close()
        
