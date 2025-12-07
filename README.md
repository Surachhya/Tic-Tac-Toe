# Tic-Tac-Toe (Multiplayer Over Sockets)

This project is a multiplayer Tic-Tac-Toe game built in Python, supporting both:

1. Terminal-based client/server
2. Tkinter GUI client/server

Players connect over a local network and take turns playing in real time. The server handles all game logic, synchronization, and communication between clients.

# Project Structure
```bash
TIC-TAC-TOE/
│
├── CPP/                      # Legacy C++ version (deprecated)
│
└── Python/
    ├── terminal/             # Terminal-only implementation
    │   ├── client.py
    │   └── server.py
    │
    └── ui/                   # Tkinter GUI implementation (recommended)
        ├── client.py
        └── server.py
```

# Requirements
Python 3.8+
Tkinter (comes preinstalled with most Python distributions)
Clients must be on the same local network as the server
No additional packages are required—this project uses only the Python standard library.

# How to Run (Tkinter GUI Version — Recommended)

Run these commands from the project root or navigate manually.
1. Navigate to the GUI folder
cd Python/ui
2. Start the server
python server.py
3. Start Client 1 (new terminal)
python client.py
4. Start Client 2 (another terminal or another machine on the same network)
python client.py

Both clients must be on the same local network and connect to the server’s IP address.

# Running the Terminal Version (Optional)
If you want a simpler, text-only experience:
cd Python/terminal
python server.py
python client.py   # Run twice for two players

# How to Play
- The server waits for two clients to join.
- Each client is assigned X or O.
- Players take turns clicking (GUI) or typing numbers 1–9 (terminal).
- The server validates moves, updates game state, and sends updates to both players.
- Games end with win, loss, or draw, and players may restart or quit the game.
