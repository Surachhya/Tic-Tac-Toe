import socket
import threading

HOST = "0.0.0.0"
PORT = 12345

board = [" "] * 9
players = []    #Connected users
symbols = ["X", "O"]    #Player 1 uses X and Player 2 uses O.
turn = 0
lock = threading.Lock()     #Safely share the game state


def board_string():     #Text version of board to be printed
    b = board
    return (
        f"\n"
        f" {b[0]} | {b[1]} | {b[2]} \n"
        f"---+---+---\n"
        f" {b[3]} | {b[4]} | {b[5]} \n"
        f"---+---+---\n"
        f" {b[6]} | {b[7]} | {b[8]} \n"
    )


def check_winner(sym):  #All winning combinations
    wins = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    return any(board[a] == board[b] == board[c] == sym for a,b,c in wins)


def client_thread(sock, idx):   #Each connected client runs inside its own thread
    global turn, players 
    symbol = symbols[idx]

    sock.sendall(f"YOUR SYMBOL {symbol}\n".encode())    #Notify client of their symbol, X or O

    while True:     #Wait state until both players are connected before game starts
        with lock:
            if len(players) == 2:
                break

    other = players[1 - idx]    #Both players are now present, can refer to each other

    if idx == 0:    #Ensure the game starts once, when client one thread runs
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
                if idx != turn:     #Only current player can make a move
                    sock.sendall(b"NOT_YOUR_TURN\n")
                    continue

                if not msg.isdigit():   #Move must be a numerical value
                    sock.sendall(b"INVALID\n")
                    continue

                pos = int(msg)

                if pos < 1 or pos > 9 or board[pos-1] != " ":   #Move only valid if in range and empty
                    sock.sendall(b"INVALID\n")
                    continue

                board[pos-1] = symbol   #Update board with current player symbol

                for p in players:
                    p.sendall(board_string().encode())  #Updated board sent to both players

                if check_winner(symbol):
                    sock.sendall(b"YOU_WIN\n")
                    other.sendall(b"YOU_LOSE\n")
                    break

                if " " not in board:
                    for p in players:
                        p.sendall(b"DRAW\n")
                    break

                turn = 1 - turn     #Alternate player turn
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

    while len(players) < 2:     #Accept 2 players
        sock, addr = server.accept()    #Start thread for each player
        print("Player connected:", addr)

        players.append(sock)
        idx = len(players) - 1

        threading.Thread(target=client_thread, args=(sock, idx), daemon=True).start()

    threading.Event().wait()    #Server stays alive for game to continue


if __name__ == "__main__":
    main()
