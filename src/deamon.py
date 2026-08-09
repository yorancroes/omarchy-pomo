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
            "START": self.start_timer,
            "PAUSE": self.pause_timer,
            "RESUME": self.resume_timer,
            "PING": self.send_message,
        }

        func = functions.get(message)
        if func is None:
            return self.send_error(conn)
        return func(conn)

    def start_timer(self, conn: socket.socket):
        if self.timer.start():
            self.send_message(conn)
        else:
            self.send_error(conn, error_msg="timer already started")

    def pause_timer(self, conn: socket.socket):
        if self.timer.pause():
            self.send_message(conn)
        else:
            self.send_error(conn, error_msg="timer isn't running")

    def resume_timer(self, conn: socket.socket):
        if self.timer.resume():
            self.send_message(conn)
        else:
            self.send_error(conn, error_msg="timer isn't paused")

    def send_message(self, conn: socket.socket):
        conn.sendall("OK".encode())

    def send_error(self, conn: socket.socket, error_msg: str = "ERROR unknown operation"):
        conn.sendall(error_msg.encode())
