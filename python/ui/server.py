import socket
import threading

HOST = "0.0.0.0"
PORT = 12345

lock = threading.Lock()
players = []  # list of (socket, symbol)
board = [" "] * 9
turn_idx = 0  # 0=X, 1=O

def log(msg):
    print(msg)

def broadcast(msg, exclude=None):
    for sock, _ in players:
        if sock != exclude:
            try:
                sock.sendall(msg.encode())
            except:
                pass

def check_winner(sym):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    return any(all(board[i]==sym for i in combo) for combo in wins)

def handle_client(sock, symbol):
    global turn_idx
    sock.sendall(f"SYMBOL {symbol}\n".encode())
    log(f"Sent symbol {symbol} to client")

    while True:
        try:
            data = sock.recv(1024)
            if not data:
                log(f"Client {symbol} disconnected")
                break
            msg = data.decode().strip()
            log(f"Received from {symbol}: {msg}")

            if not msg.isdigit():
                sock.sendall(b"INVALID\n")
                continue
            pos = int(msg) - 1
            if pos < 0 or pos > 8:
                sock.sendall(b"INVALID\n")
                continue

            with lock:
                # Check turn
                if players[turn_idx][0] != sock:
                    sock.sendall(b"NOT_YOUR_TURN\n")
                    log(f"Ignored move from {symbol}: not your turn")
                    continue
                # Check position
                if board[pos] != " ":
                    sock.sendall(b"INVALID\n")
                    log(f"Ignored move from {symbol}: position {pos+1} taken")
                    continue

                # Valid move
                board[pos] = symbol
                sock.sendall(f"MOVE_OK {pos+1} {symbol}\n".encode())
                broadcast(f"UPDATE {pos+1} {symbol}\n", exclude=sock)
                log(f"{symbol} played position {pos+1}")

                # Check win
                if check_winner(symbol):
                    sock.sendall(b"YOU_WIN\n")
                    broadcast("YOU_LOSE\n", exclude=sock)
                    log(f"Player {symbol} wins")
                    break
                # Check draw
                if " " not in board:
                    for s,_ in players:
                        s.sendall(b"DRAW\n")
                    log("Game draw")
                    break

                # Switch turn
                turn_idx = 1 - turn_idx
                next_sock, next_sym = players[turn_idx]
                next_sock.sendall(b"YOUR_TURN\n")
                log(f"Turn switched to {next_sym}")

        except Exception as e:
            log(f"Client {symbol} error: {e}")
            break

    sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    log(f"Server listening on port {PORT}...")

    symbols = ["X", "O"]

    # Accept exactly 2 clients
    while len(players) < 2:
        sock, addr = server.accept()
        symbol = symbols[len(players)]
        players.append((sock, symbol))
        log(f"Player connected from {addr} as {symbol}")
        threading.Thread(target=handle_client, args=(sock, symbol), daemon=True).start()

    # Start game
    for s,_ in players:
        s.sendall(b"START\n")
    players[turn_idx][0].sendall(b"YOUR_TURN\n")
    log(f"Player {players[turn_idx][1]} turn")

    threading.Event().wait()  # Keep server alive

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
