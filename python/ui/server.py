import socket
import threading

# Server will listen on all network interfaces
HOST = "0.0.0.0"
PORT = 12345

# Lock ensures only one thread updates shared game state at a time
lock = threading.Lock()

# List to store connected players as (socket, symbol)
players = []

# Represents the 3x3 board as a flat list of 9 spaces
board = [" "] * 9

# Whose turn it is: 0 = X, 1 = O
turn_idx = 0

# Simple logging function to show activity in server terminal
def log(msg):
    print(msg)

# Send a message to all players except the one who sent it (if exclude provided)
def broadcast(msg, exclude=None):
    for sock, _ in players:
        if sock != exclude:
            try:
                sock.sendall(msg.encode())
            except:
                # Ignore if sending fails (player disconnected)
                pass

# Check if a player with given symbol has won
def check_winner(sym):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),  # Rows
        (0,3,6),(1,4,7),(2,5,8),  # Columns
        (0,4,8),(2,4,6)           # Diagonals
    ]
    return any(all(board[i]==sym for i in combo) for combo in wins)

# Handles communication and moves for one player
def receive_move(sock, symbol):
    #Receive and validate a move from the client.
    data = sock.recv(1024)
    if not data:
        return None
    msg = data.decode().strip()
    log(f"Received from {symbol}: {msg}")
    if not msg.isdigit():
        sock.sendall(b"INVALID\n")
        return None
    pos = int(msg) - 1
    if pos < 0 or pos > 8:
        sock.sendall(b"INVALID\n")
        return None
    return pos

def make_move(pos, symbol, sock):
    #Apply the move to the board and notify all clients.
    board[pos] = symbol
    sock.sendall(f"MOVE_OK {pos+1} {symbol}\n".encode())
    broadcast(f"UPDATE {pos+1} {symbol}\n", exclude=sock)
    log(f"{symbol} played position {pos+1}")

def check_game_status(symbol, sock):
    # Check win/draw and notify clients if game ended.
    if check_winner(symbol):
        sock.sendall(b"YOU_WIN\n")
        broadcast("YOU_LOSE\n", exclude=sock)
        log(f"Player {symbol} wins")
        return True
    if " " not in board:
        for s,_ in players:
            s.sendall(b"DRAW\n")
        log("Game draw")
        return True
    return False

def switch_turn():
    # Switch turn to the next player and notify them.
    global turn_idx
    turn_idx = 1 - turn_idx
    next_sock, next_sym = players[turn_idx]
    next_sock.sendall(b"YOUR_TURN\n")
    log(f"Turn switched to {next_sym}")

# --- Main client handler ---
def handle_client(sock, symbol):
    global turn_idx
    sock.sendall(f"SYMBOL {symbol}\n".encode())
    log(f"Sent symbol {symbol} to client")

    while True:
        try:
            pos = receive_move(sock, symbol)
            if pos is None:
                continue  # invalid or non-digit input
            with lock:
                # Check turn
                if players[turn_idx][0] != sock:
                    sock.sendall(b"NOT_YOUR_TURN\n")
                    log(f"Ignored move from {symbol}: not your turn")
                    continue
                # Check if position already taken
                if board[pos] != " ":
                    sock.sendall(b"INVALID\n")
                    log(f"Ignored move from {symbol}: position {pos+1} taken")
                    continue

                # Valid move
                make_move(pos, symbol, sock)

                # Check if game ended
                if check_game_status(symbol, sock):
                    break

                # Switch turn
                switch_turn()

        except Exception as e:
            log(f"Client {symbol} error: {e}")
            break

    sock.close()

# Main server function
def main():
    # Create a TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)  # Wait for two clients
    log(f"Server listening on port {PORT}...")

    symbols = ["X", "O"]

    # Accept exactly two players
    while len(players) < 2:
        sock, addr = server.accept()
        symbol = symbols[len(players)]
        players.append((sock, symbol))
        log(f"Player connected from {addr} as {symbol}")
        # Start a separate thread to handle this player
        threading.Thread(target=handle_client, args=(sock, symbol), daemon=True).start()

    # Let both players know the game is starting
    for s,_ in players:
        s.sendall(b"START\n")

    # Give first turn to X
    players[turn_idx][0].sendall(b"YOUR_TURN\n")
    log(f"Player {players[turn_idx][1]} turn")

    # Keep server running indefinitely
    threading.Event().wait()

# Entry point
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
