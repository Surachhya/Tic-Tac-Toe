import socket
import threading

HOST = "127.0.0.1"
PORT = 12345


def listen(server):
    # This thread listens for messages from the server.
    # Anything printed here shows up instantly on the player's screen.
    while True:
        msg = server.recv(1024)
        if not msg:
            print("Server closed connection.")
            break

        msg = msg.decode()

        # When the server says it is your turn, show a clearer prompt.
        if "YOUR_TURN" in msg:
            print("\nYour turn. Enter a position from 1 to 9:")
        else:
            print(msg)
            print("\nOther player's turn. Please wait...")


def main():
    # Connect to the server.
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Start a listener thread so messages from the server appear instantly.
    threading.Thread(target=listen, args=(client,), daemon=True).start()

    # Main input loop for sending moves to the server.
    while True:
        user_input = input()
        if user_input == "":
            continue
        client.sendall(user_input.encode())


if __name__ == "__main__":
    main()
