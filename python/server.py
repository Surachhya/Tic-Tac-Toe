import socket
import threading

HOST = "0.0.0.0"
PORT = 12345

board = [" "] * 9
players = []
symbols = ["X", "O"]
turn = 0  # whose turn? 0 = X, 1 = O

lock = threading.Lock()

def board_string():
    b = board
    return (
        f"\n"
        f" {b[0]} | {b[1]} | {b[2]} \n"
        f"---+---+---\n"
        f" {b[3]} | {b[4]} | {b[5]} \n"
        f"---+---+---\n"
        f" {b[6]} | {b[7]} | {b[8]} \n"
    )

def check_winner(sym):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    return any(board[a] == board[b] == board[c] == sym for a,b,c in wins)

def client_thread(sock, idx):
    global turn, players

    symbol = symbols[idx]

    # Send symbol
    sock.sendall(f"SYMBOL {symbol}\n".encode())

    # 🔥 FIX: Wait for two players BEFORE accessing players[1 - idx]
    while True:
        with lock:
            if len(players) == 2:
                break

    # Both players connected now
    other = players[1 - idx]

    # Start game once
    if idx == 0:  # only let player 1 start game once
        for p in players:
            p.sendall(b"START\n")
            p.sendall(board_string().encode())
        players[turn].sendall(b"YOUR_TURN\n")

    while True:
        try:
            msg = sock.recv(1024)
            if not msg:
                break
            msg = msg.decode().strip()

            with lock:
                if idx != turn:
                    sock.sendall(b"NOT_YOUR_TURN\n")
                    continue

                # Validate move
                if not msg.isdigit():
                    sock.sendall(b"INVALID\n")
                    continue

                pos = int(msg)
                if pos < 1 or pos > 9 or board[pos-1] != " ":
                    sock.sendall(b"INVALID\n")
                    continue

                # Make move
                board[pos-1] = symbol

                # Send updated board
                for p in players:
                    p.sendall(board_string().encode())

                # Win
                if check_winner(symbol):
                    sock.sendall(b"YOU_WIN\n")
                    other.sendall(b"YOU_LOSE\n")
                    break

                # Draw
                if " " not in board:
                    for p in players:
                        p.sendall(b"DRAW\n")
                    break

                # Switch turn
                turn = 1 - turn
                players[turn].sendall(b"YOUR_TURN\n")

        except:
            break

    sock.close()

def main():
    global players
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)

    print(f"Server listening on port {PORT}...")

    while len(players) < 2:
        sock, addr = server.accept()
        print("Player connected:", addr)

        players.append(sock)
        idx = len(players) - 1
        threading.Thread(target=client_thread, args=(sock, idx), daemon=True).start()

    # Server stays alive until threads finish
    threading.Event().wait()

if __name__ == "__main__":
    main()
