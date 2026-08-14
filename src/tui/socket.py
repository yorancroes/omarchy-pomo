import socket


def create_socket():
    path = "/tmp/pomodoro.sock"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(path)
    return s


def send_command(command: str):
    available_commands = {
        "start": "START\n",
        "pause": "PAUSE\n",
        "skip": "SKIP\n",
    }

    try:
        s = create_socket()

    except ConnectionRefusedError as e:
        return f"ERROR: failed to connect to socket: {e}"

    except FileNotFoundError as e:
        return f"ERROR: socket file not found: {e}"

    msg = available_commands.get(command)

    if msg is not None:
        s.sendall(msg.encode())
    else:
        return "ERROR: command not available try: start, pause "

    data = s.recv(1024)
    return data.decode()
