import socket

path = "/tmp/echo.sock"

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(path)

message = "hello ik ben cool"

s.sendall(message.encode())
data = s.recv(1024)

print(data.decode())
