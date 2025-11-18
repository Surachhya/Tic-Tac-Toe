import socket
import threading
import tkinter as tk
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 12345

class TicTacToeClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic-Tac-Toe")
        self.symbol = None
        self.my_turn = False
        self.buttons = []

        # Info label
        self.info_label = tk.Label(master, text="Connecting...", font=("Arial", 14))
        self.info_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Create buttons 3x3
        for i in range(3):
            row_buttons = []
            for j in range(3):
                btn = tk.Button(master, text=" ", font=("Arial", 24), width=5, height=2,
                                command=lambda r=i, c=j: self.click_cell(r, c))
                btn.grid(row=i+1, column=j, padx=5, pady=5)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        # Connect to server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        pos = row*3 + col +1
        self.client.sendall(str(pos).encode())
        print(f"Sent move: {pos}")
        # Immediately update button to show user click
        btn["text"] = self.symbol
        btn["state"] = "disabled"
        self.my_turn = False
        self.info_label.config(text="Opponent's turn...")

    def listen_server(self):
        while True:
            try:
                data = self.client.recv(1024)
                if not data:
                    break
                for msg in data.decode().strip().splitlines():
                    self.master.after(0, self.process_message, msg.strip())
            except:
                break
        self.master.after(0, lambda: messagebox.showinfo("Disconnected", "Server closed connection"))
        self.master.after(0, self.master.destroy)

    def process_message(self, msg):
        print(f"Received: {msg}")
        if msg.startswith("SYMBOL"):
            self.symbol = msg.split()[1]
            self.info_label.config(text=f"Your symbol: {self.symbol}")
        elif msg == "START":
            self.info_label.config(text="Game started. Waiting for turn...")
        elif msg == "YOUR_TURN":
            self.my_turn = True
            self.info_label.config(text="Your turn!")
            for i in range(3):
                for j in range(3):
                    if self.buttons[i][j]["text"] == " ":
                        self.buttons[i][j]["state"] = "normal"
        elif msg.startswith("UPDATE"):
            _, pos, sym = msg.split()
            pos = int(pos)-1
            row, col = divmod(pos, 3)
            self.buttons[row][col]["text"] = sym
            self.buttons[row][col]["state"] = "disabled"
        elif msg.startswith("MOVE_OK"):
            pass  # Already updated locally
        elif msg == "NOT_YOUR_TURN":
            self.my_turn = False
            self.info_label.config(text="Opponent's turn...")
        elif msg == "YOU_WIN":
            self.my_turn = False
            messagebox.showinfo("Game Over", "You Win!")
        elif msg == "YOU_LOSE":
            self.my_turn = False
            messagebox.showinfo("Game Over", "You Lose!")
        elif msg == "DRAW":
            self.my_turn = False
            messagebox.showinfo("Game Over", "Draw!")

if __name__ == "__main__":
    root = tk.Tk()
    TicTacToeClient(root)
    root.mainloop()
