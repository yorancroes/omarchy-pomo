import os
import socket

path = "/tmp/echo.sock"
if os.path.exists(path):
    os.remove(path)
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(path)
s.listen()
conn, addr = s.accept()

data = conn.recv(1024)
message = data.decode()
conn.sendall(message.encode())

conn.close()
s.close()
