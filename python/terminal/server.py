import socket
import threading

HOST = "0.0.0.0"
PORT = 12345

# The tic-tac-toe board is stored as a list of 9 positions.
board = [" "] * 9

# Connected players will be stored in this list.
players = []

# Player 1 uses X and Player 2 uses O.
symbols = ["X", "O"]

# Keeps track of whose turn it is. Zero means X starts.
turn = 0

# A lock is used so the threads can safely share the game state.
lock = threading.Lock()


def board_string():
    # Creates a simple text version of the board that can be printed
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
    # Lists all winning combinations. The function checks if any match the player symbol.
    wins = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    return any(board[a] == board[b] == board[c] == sym for a,b,c in wins)


def client_thread(sock, idx):
    # Each connected client runs inside its own thread.
    global turn, players

    symbol = symbols[idx]

    # Let the client know whether it is X or O.
    sock.sendall(f"YOUR SYMBOL {symbol}\n".encode())

    # Wait until both players are connected before trying to start the game.
    while True:
        with lock:
            if len(players) == 2:
                break

    # Both players are present, so each client can refer to the other now.
    other = players[1 - idx]

    # Start the game only one time, when the first client thread runs.
    if idx == 0:
        for p in players:
            p.sendall(b"START\n")
            p.sendall(board_string().encode())
        players[turn].sendall(b"YOUR_TURN\n")

    # Main loop that keeps listening for moves from the client.
    while True:
        try:
            msg = sock.recv(1024)
            if not msg:
                break
            msg = msg.decode().strip()

            with lock:
                # Only the current player may make a move.
                if idx != turn:
                    sock.sendall(b"NOT_YOUR_TURN\n")
                    continue

                # Make sure the move is a number.
                if not msg.isdigit():
                    sock.sendall(b"INVALID\n")
                    continue

                pos = int(msg)

                # Check if the move is in range and the spot is empty.
                if pos < 1 or pos > 9 or board[pos-1] != " ":
                    sock.sendall(b"INVALID\n")
                    continue

                # Update the board with the player's symbol.
                board[pos-1] = symbol

                # Send the new board to both players.
                for p in players:
                    p.sendall(board_string().encode())

                # Check if the move wins the game.
                if check_winner(symbol):
                    sock.sendall(b"YOU_WIN\n")
                    other.sendall(b"YOU_LOSE\n")
                    break

                # Check if all spaces are filled with no winner.
                if " " not in board:
                    for p in players:
                        p.sendall(b"DRAW\n")
                    break

                # Switch the turn to the other player.
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

    # The server accepts two players and starts a thread for each.
    while len(players) < 2:
        sock, addr = server.accept()
        print("Player connected:", addr)

        players.append(sock)
        idx = len(players) - 1

        threading.Thread(target=client_thread, args=(sock, idx), daemon=True).start()

    # The server stays alive so the game can continue.
    threading.Event().wait()


if __name__ == "__main__":
    main()
