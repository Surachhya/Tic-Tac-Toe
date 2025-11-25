import socket
import threading
import tkinter as tk
from tkinter import messagebox

HOST = "172.20.10.2" # Server IP address (we need to copy from wifi details)
PORT = 12345 # this also needs to match the server port

class TicTacToeClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic-Tac-Toe")
        self.symbol = None
        self.my_turn = False
        self.buttons = []
        self.last_move = None

        self.info_label = tk.Label(master, text="Connecting...", font=("Arial", 14))
        self.info_label.grid(row=0, column=0, columnspan=3, pady=10)

        self.restart_btn = tk.Button(master, text="Restart", font=("Arial", 12), command=self.restart_game)
        self.restart_btn.grid(row=4, column=0, columnspan=3, pady=5)

        self.quit_btn = tk.Button(master, text="Quit Game", font=("Arial", 12), command=self.quit_game)
        self.quit_btn.grid(row=5, column=0, columnspan=3, pady=5)

        for i in range(3):
            row_buttons = []
            for j in range(3):
                btn = tk.Button(master, text=" ", font=("Arial", 24), width=5, height=2,
                                command=lambda r=i, c=j: self.click_cell(r, c))
                btn.grid(row=i+1, column=j, padx=5, pady=5)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     #Connect to server
        try:
            self.client.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect: {e}")
            master.destroy()
            return

        threading.Thread(target=self.listen_server, daemon=True).start()

    def click_cell(self, row, col):
        if not self.my_turn:
            print("Ignored click: not your turn")
            return
        btn = self.buttons[row][col]
        if btn["text"] != " ":
            print("Ignored click: cell occupied")
            return

        pos = row * 3 + col + 1
        self.client.sendall(str(pos).encode())
        print(f"Sent move: {pos}")

        btn["text"] = self.symbol
        btn["state"] = "disabled"
        self.my_turn = False
        self.info_label.config(text="Opponent's turn...")

        if self.last_move:
            self.last_move["bg"] = "SystemButtonFace"
        btn["bg"] = "lightgreen"
        self.last_move = btn

    def listen_server(self):
        while True:
            try:
                data = self.client.recv(1024)
                if not data:
                    break
                for msg in data.decode().strip().splitlines():
                    if getattr(self, "game_over", False):
                        continue    #Ignore messages after game over
                    self.master.after(0, self.process_message, msg.strip())
            except:
                break


    def process_message(self, msg):
        print(f"Received: {msg}")
        if msg.startswith("SYMBOL"):
            self.symbol = msg.split()[1]
            self.info_label.config(text=f"Your symbol: {self.symbol}")
        elif msg == "START":
            self.info_label.config(text="Game started. Waiting for turn...")
            self.reset_board()
        elif msg == "YOUR_TURN":
            self.my_turn = True
            self.info_label.config(text="Your turn!")
            self.enable_empty_buttons()
        elif msg.startswith("UPDATE"): #Update board with opponent move
            _, pos, sym = msg.split()
            pos = int(pos)-1
            row, col = divmod(pos, 3)
            btn = self.buttons[row][col]
            btn["text"] = sym
            btn["state"] = "disabled"

            if self.last_move:  #Highlights opponent move
                self.last_move["bg"] = "SystemButtonFace"
            btn["bg"] = "lightblue"
            self.last_move = btn
        elif msg.startswith("MOVE_OK"):
            pass  #Already updated locally
        elif msg == "NOT_YOUR_TURN":
            self.my_turn = False
            self.info_label.config(text="Opponent's turn...")
            self.disable_all_buttons()
        elif msg in ["YOU_WIN", "YOU_LOSE", "DRAW"]:
            self.my_turn = False
            result_text = {"YOU_WIN":"Hurray, You Win!", "YOU_LOSE":"Sorry, You Lose!", "DRAW":"Draw!"}[msg]
            result_text = f"Game Over: Player {self.symbol} : {result_text}"
            messagebox.showinfo("Game Over", result_text)
            self.disable_all_buttons()
        elif msg == "OPPONENT_QUIT":
            messagebox.showinfo("Game Over", "Your opponent has quit the game.")
            self.disable_all_buttons()
            self.quit_game()    #Exit game completely after quitting
            #return

    def reset_board(self):
        for row in self.buttons:
            for btn in row:
                btn["text"] = " "
                btn["state"] = "disabled"
                btn["bg"] = "SystemButtonFace"
        self.last_move = None

    def enable_empty_buttons(self):
        for row in self.buttons:
            for btn in row:
                if btn["text"] == " ":
                    btn["state"] = "normal"

    def disable_all_buttons(self):
        for row in self.buttons:
            for btn in row:
                btn["state"] = "disabled"
    
    def restart_game(self):     #Reset board locally and tell server to restart
        self.reset_board()
        self.info_label.config(text="Restart requested")
        self.client.sendall(b"RESTART\n")

    def quit_game(self):
        self.client.sendall(b"QUIT\n")
        print("Sent quit message to server")
        self.client.close()     #Close client connection
        self.master.quit()      #Closes window

if __name__ == "__main__":
    root = tk.Tk()
    TicTacToeClient(root)
    root.mainloop()
