import socket
import threading

HOST = "127.0.0.1"
PORT = 12345


def listen(server):
    while True:
        msg = server.recv(1024)
        if not msg:
            print("Server closed connection.")
            break

        msg = msg.decode()

        if "YOUR_TURN" in msg:
            print("\n➡ Your turn! Enter position (1-9):")
        else:
            print(msg)


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    threading.Thread(target=listen, args=(client,), daemon=True).start()

    while True:
        user_input = input()
        if user_input == "":
            continue
        client.sendall(user_input.encode())


if __name__ == "__main__":
    main()
