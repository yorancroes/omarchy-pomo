import sys

from tui.socket import send_command, send_time_command


def main():

    if len(sys.argv) == 1:
        print("ERROR: no command was given")
        return

    elif len(sys.argv) == 2:
        command = sys.argv[1]
        print(send_command(command))

    elif len(sys.argv) == 3:
        command = sys.argv[1] + " " + sys.argv[2]
        print(send_time_command(command))


if __name__ == "__main__":
    main()
