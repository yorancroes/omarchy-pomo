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
        return "ERROR: command not available try: start, pause, change_break [time_in_seconds], change_pomo [time_in_seconds]"

    data = s.recv(1024)
    return data.decode()


def send_time_command(command: str):
    command_list = command.split()
    print(command_list)

    available_commands = {
        "change_break": "CHANGE_BREAK",
        "change_pomo": "CHANGE_POMO",
    }

    try:
        s = create_socket()

    except ConnectionRefusedError as e:
        return f"ERROR: failed to connect to socket: {e}"

    except FileNotFoundError as e:
        return f"ERROR: socket file not found: {e}"

    command = available_commands.get(command_list[0])

    if command is None:
        return "Error wrong command"
    msg = command + " " + command_list[1] + "\n"

    if msg is not None:
        s.sendall(msg.encode())
    else:
        return "ERROR: command not available try: start, pause, change_break [time_in_seconds], change_pomo [time_in_seconds]"

    data = s.recv(1024)
    return data.decode()
