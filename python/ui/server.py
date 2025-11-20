import socket
import threading

HOST = "0.0.0.0"
PORT = 12345

lock = threading.Lock()     #Ensure only one thread updates shared game state at a time

players = []    #Store connected players
board = [" "] * 9
turn_idx = 0    #0 = X, 1 = O

def log(msg):   #Shows activity in server terminal
    print(msg)

def broadcast(msg, exclude=None):
    for sock, _ in players:
        if sock != exclude:
            try:
                sock.sendall(msg.encode())
            except:
                pass    #Ignore if sending fails (player disconnected)

def check_winner(sym):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),  #Rows
        (0,3,6),(1,4,7),(2,5,8),  #Columns
        (0,4,8),(2,4,6)           #Diagonals
    ]
    return any(all(board[i]==sym for i in combo) for combo in wins)

def receive_move(sock, symbol): #Commmunication and moves for current player
    data = sock.recv(1024)
    if not data:
        return None
    msg = data.decode().strip()
    log(f"Received from {symbol}: {msg}")
    if msg.upper() == "RESTART":
        return "RESTART"
    if not msg.isdigit():
        sock.sendall(b"INVALID\n")
        return None
    pos = int(msg) - 1
    if pos < 0 or pos > 8:
        sock.sendall(b"INVALID\n")
        return None
    return pos

def reset_board_and_notify_clients():
    global board, turn_idx

    with lock:
        board = [" "] * 9   #Reset board
        turn_idx = 0        #Reset turn

        for sock, symbol in players:    #Notify both players
            try:
                sock.sendall(b"START\n")
                sock.sendall(f"SYMBOL {symbol}\n".encode())
            except Exception as e:
                print(f"Error sending reset to {symbol}: {e}")

        try:
            first_sock, first_symbol = players[turn_idx]    #Player one's turn
            first_sock.sendall(b"YOUR_TURN\n")
            print(f"Board reset. Player {first_symbol} turn")
        except Exception as e:
            print(f"Error notifying first turn: {e}")


def make_move(pos, symbol, sock):
    board[pos] = symbol     #Apply move
    sock.sendall(f"MOVE_OK {pos+1} {symbol}\n".encode())
    broadcast(f"UPDATE {pos+1} {symbol}\n", exclude=sock)   #Notify clients
    log(f"{symbol} played position {pos+1}")

def check_game_status(symbol, sock):
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
    global turn_idx
    turn_idx = 1 - turn_idx
    next_sock, next_sym = players[turn_idx]
    next_sock.sendall(b"YOUR_TURN\n")
    log(f"Turn switched to {next_sym}")

def handle_client(sock, symbol):
    global turn_idx
    sock.sendall(f"SYMBOL {symbol}\n".encode())
    log(f"Sent symbol {symbol} to client")

    while True:
        try:
            pos = receive_move(sock, symbol)
            if pos == "RESTART":
                reset_board_and_notify_clients()
                continue
            if pos is None:
                continue  #Invalid or non-digit input
            with lock:
                if players[turn_idx][0] != sock:
                    sock.sendall(b"NOT_YOUR_TURN\n")
                    log(f"Ignored move from {symbol}: not your turn")
                    continue
                if board[pos] != " ":
                    sock.sendall(b"INVALID\n")
                    log(f"Ignored move from {symbol}: position {pos+1} taken")
                    continue

                make_move(pos, symbol, sock)    #Valid move
                check_game_status(symbol, sock) #Checks if game has ended
                switch_turn()                   #Next player turn

        except Exception as e:
            log(f"Client {symbol} error: {e}")
            break

    sock.close()

def handle_quit(sock, symbol):
    print(f"Player {symbol} has quit the game.")

    for s, _ in players:
        if s != sock:
            s.sendall(b"OPPONENT_QUIT\n")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)    #Wait for two clients
    log(f"Server listening on port {PORT}...")

    symbols = ["X", "O"]

    while len(players) < 2: #Only 2 players allowed
        sock, addr = server.accept()
        symbol = symbols[len(players)]
        players.append((sock, symbol))
        log(f"Player connected from {addr} as {symbol}")
        threading.Thread(target=handle_client, args=(sock, symbol), daemon=True).start()    #Separate thread to handle player

    for s,_ in players:     #Notify both players of game start
        s.sendall(b"START\n")

    players[turn_idx][0].sendall(b"YOUR_TURN\n")
    log(f"Player {players[turn_idx][1]} turn")

    threading.Event().wait()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
