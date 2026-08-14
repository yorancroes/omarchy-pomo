import socket

SOCKET_PATH = "/tmp/pomodoro.sock"


def send(command: str) -> str:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(SOCKET_PATH)
        s.sendall(f"{command}\n".encode())
        return s.recv(1024).decode()


def main():
    try:
        response = send("START")
    except (ConnectionRefusedError, FileNotFoundError):
        return

    if response.startswith("ERROR"):
        send("PAUSE")


if __name__ == "__main__":
    main()
