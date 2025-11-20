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

        #Prompts for user turn stages
        if "YOUR_TURN" in msg:
            print("\nYour turn. Enter a position from 1 to 9:")
        else:
            print(msg)
            print("\nOther player's turn. Please wait...")


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    #Starts a listener thread from server
    threading.Thread(target=listen, args=(client,), daemon=True).start()

    #Loop for sending moves to server
    while True:
        user_input = input()
        if user_input == "":
            continue
        client.sendall(user_input.encode())


if __name__ == "__main__":
    main()
