#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <sstream>
#include "asio.hpp"

using asio::ip::tcp;

const int BOARD_SIZE = 3;

struct Player {
    std::shared_ptr<tcp::socket> socket;
    char symbol;
};

void print_board(const char board[BOARD_SIZE][BOARD_SIZE]) {
    std::cout << "\nBoard State:\n";
    for (int i = 0; i < BOARD_SIZE; ++i) {
        for (int j = 0; j < BOARD_SIZE; ++j) {
            std::cout << (board[i][j] ? board[i][j] : '.') << ' ';
        }
        std::cout << "\n";
    }
}

bool check_win(const char board[BOARD_SIZE][BOARD_SIZE], char sym) {
    for (int i = 0; i < BOARD_SIZE; ++i)
        if (board[i][0]==sym && board[i][1]==sym && board[i][2]==sym) return true;
    for (int j = 0; j < BOARD_SIZE; ++j)
        if (board[0][j]==sym && board[1][j]==sym && board[2][j]==sym) return true;
    if (board[0][0]==sym && board[1][1]==sym && board[2][2]==sym) return true;
    if (board[0][2]==sym && board[1][1]==sym && board[2][0]==sym) return true;
    return false;
}

bool check_draw(const char board[BOARD_SIZE][BOARD_SIZE]) {
    for(int i=0;i<BOARD_SIZE;i++)
        for(int j=0;j<BOARD_SIZE;j++)
            if(board[i][j]=='\0') return false;
    return true;
}

int main() {
    try {
        asio::io_context io_context;
        tcp::acceptor acceptor(io_context, tcp::endpoint(tcp::v4(), 12345));

        std::vector<Player> players;
        char symbols[2] = {'X','O'};

        std::cout << "Server listening on port 12345...\n";

        // Accept 2 clients
        while(players.size() < 2) {
            auto sock = std::make_shared<tcp::socket>(io_context);
            acceptor.accept(*sock);
            char sym = symbols[players.size()];
            players.push_back({sock, sym});

            std::string assign_msg = "ASSIGN ";
            assign_msg += sym;
            assign_msg += "\n";
            asio::write(*sock, asio::buffer(assign_msg));

            std::cout << "Client " << players.size() << " connected as " << sym << "\n";
        }

        // Initialize empty board
        char board[BOARD_SIZE][BOARD_SIZE] = {};
        std::cout << "Both clients connected. Starting game...\n";

        int turn = 0;
        bool game_over = false;

        while(!game_over) {
            Player& current = players[turn % 2];
            Player& other = players[(turn+1)%2];

            // Notify current player
            asio::write(*current.socket, asio::buffer("YOUR_TURN\n"));

            // Receive move
            char data[1024];
            size_t len = current.socket->read_some(asio::buffer(data));
            std::string move_str(data,len);
            std::istringstream iss(move_str);
            int row, col;
            char comma;
            iss >> row >> comma >> col;

            // Validate move
            if(row<0 || row>=BOARD_SIZE || col<0 || col>=BOARD_SIZE || board[row][col]!='\0') {
                asio::write(*current.socket, asio::buffer("INVALID_MOVE\n"));
                continue; // retry
            }

            board[row][col] = current.symbol;
            print_board(board);

            // Broadcast move
            std::string update = "UPDATE_BOARD " + std::to_string(row) + "," + std::to_string(col) + "," + current.symbol + "\n";
            for(auto& p : players) {
                asio::write(*p.socket, asio::buffer(update));
            }

            // Check win/draw
            if(check_win(board, current.symbol)) {
                std::string msg = "GAME_OVER WIN\n";
                asio::write(*current.socket, asio::buffer(msg));
                asio::write(*other.socket, asio::buffer("GAME_OVER LOSE\n"));
                game_over = true;
            } else if(check_draw(board)) {
                for(auto& p : players)
                    asio::write(*p.socket, asio::buffer("GAME_OVER DRAW\n"));
                game_over = true;
            } else {
                turn++;
            }
        }

        std::cout << "Game session ended.\n";

    } catch(std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
    }
    return 0;
}
