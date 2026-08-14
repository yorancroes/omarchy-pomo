import sys
import socket


def create_socket():
    path = "/tmp/pomodoro.sock"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(path)
    return s


def main():

    if len(sys.argv) == 1:
        print("ERROR: no command was given")
        return

    command = sys.argv[1]

    availeble_commands = {
        "start": "START\n",
        "pause": "PAUSE\n",
        "resume": "RESUME\n",
    }

    try:
        s = create_socket()

    except ConnectionRefusedError as e:
        print(f"ERROR: failed to connect to socket: {e}")
        return

    except FileNotFoundError as e:
        print(f"ERROR: socket file not found: {e}")
        return

    msg = availeble_commands.get(command)

    if msg is not None:
        s.sendall(msg.encode())
    else:
        print("ERROR: command not available try: start, pause, resume")
        return

    data = s.recv(1024)
    print(data.decode())


if __name__ == "__main__":
    main()
