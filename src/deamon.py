import os
import socket
from timer import Timer


class PomodoroDeamon:
    def __init__(self):
        self.path = "/tmp/pomodoro.sock"
        self.timer = Timer()
        self.setup()
        self.run()

    def setup(self):
        self.sock: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        if os.path.exists(self.path):
            os.remove(self.path)

        self.sock.bind(self.path)
        self.sock.listen()

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            self.handle_connection(conn)

    def handle_connection(self, conn: socket.socket):
        message = conn.recv(1024).decode()

        functions = {
            "START": self.timer.start,
            "PAUSE": self.timer.pause,
            "RESUME": self.timer.resume,
            "PING": self.send_message,
        }

    def send_message(self):
        pass
