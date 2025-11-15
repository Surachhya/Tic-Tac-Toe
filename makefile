# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Ithird_party/asio
LDFLAGS = -lws2_32

# Source files
SERVER_SRC = src/server.cpp
CLIENT_SRC = src/client.cpp
MAIN_SRC   = src/main.cpp

# Output binaries
SERVER_BIN = server.exe
CLIENT_BIN = client.exe
MAIN_BIN   = tic_tac_toe.exe

# Default target
all: $(SERVER_BIN) $(CLIENT_BIN) $(MAIN_BIN)

$(SERVER_BIN): $(SERVER_SRC)
	$(CXX) $(CXXFLAGS) $^ $(LDFLAGS) -o $@

$(CLIENT_BIN): $(CLIENT_SRC)
	$(CXX) $(CXXFLAGS) $^ $(LDFLAGS) -o $@

$(MAIN_BIN): $(MAIN_SRC)
	$(CXX) $(CXXFLAGS) $^ $(LDFLAGS) -o $@

# Clean
clean:
	rm -f $(SERVER_BIN) $(CLIENT_BIN) $(MAIN_BIN)
