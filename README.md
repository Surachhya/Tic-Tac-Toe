# Tic-Tac-Toe (Multiplayer Over Sockets)

This is a simple multiplayer Tic-Tac-Toe game built in C++ using sockets.  
It includes a **Server** and **Client** program so multiple players can connect and play from different terminals.

---

## Requirements (Windows)

Because this project uses `make`, ensure that **make** is installed on Windows.  
You can install it through:

### Option 1 — **MSYS2** (Recommended)
1. Install from https://www.msys2.org/
2. Open **MSYS2 MinGW64** terminal
3. Install tools:  
   ```sh
   pacman -S make gcc
   ```

### Option 2 — **GNU Make for Windows**
Download "make" binary and place it in `C:\Program Files\GnuWin32\bin`  
Then add it to **PATH**.

---

## How to Build & Run

Run all commands **from the project root**, where your `Makefile` is located.

### 1 Build the project
```sh
make
```

### 1 Start the Server
```sh
./Server
```

### 3 Start Client 1 (new terminal)
```sh
./Client
```

### 4 Start Client 2 (another terminal)
```sh
./Client
```

---

## How to Play ( we need to build Gui later; I am thinking using IMGUI)
 
 Instruction for now:

- Two clients connect to the server.
- The server coordinates turns and board updates.
- Players play directly **in the terminal**.
- Enter positions (1–9) when prompted.

---

## Files Overview

| File | Description |
|------|-------------|
| `Server.cpp` | Main server logic handling clients and game state |
| `Client.cpp` | Client-side interaction and user moves |
| `Makefile` | Builds Server and Client executables |

---

##  Build Notes

- The project uses Windows networking (`winsock2.h`), so make sure you link **Ws2_32**.
- The Makefile already does this:  
  ```
  -lws2_32
  ```

---

Now run the server, open two clients, and play Tic-Tac-Toe over the network.

