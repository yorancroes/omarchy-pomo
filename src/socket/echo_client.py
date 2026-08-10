import socket

path = "/tmp/pomodoro.sock"

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(path)

message = "START\n"

s.sendall(message.encode())
data = s.recv(1024)

print(data.decode())
