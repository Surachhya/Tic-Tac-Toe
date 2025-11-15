#include <iostream>
#include <string>
#include "asio.hpp"

using asio::ip::tcp;

char board[3][3]{};

void print_board()
{
    std::cout << "\nBoard State:\n";
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            std::cout << (board[i][j] ? board[i][j] : '.') << " ";
        }
        std::cout << "\n";
    }
}

int main()
{
    try
    {
        asio::io_context io_context;
        tcp::resolver resolver(io_context);
        auto endpoints = resolver.resolve("127.0.0.1", "12345");

        tcp::socket socket(io_context);
        asio::connect(socket, endpoints);

        asio::streambuf buf;
        asio::read_until(socket, buf, '\n');
        std::istream is(&buf);
        std::string msg;
        std::getline(is, msg);

        char my_symbol = msg.back();
        std::cout << "Assigned symbol: " << my_symbol << "Open or go to another client" <<"\n";

        while (true)
        {
            asio::streambuf buf;
            asio::read_until(socket, buf, '\n');

            std::istream is(&buf);
            std::string server_msg;
            std::getline(is, server_msg);


            if (server_msg.find("YOUR_TURN") != std::string::npos)
            {
                print_board();
                std::string move;
                std::cout << "Your turn (row,col): ";
                std::getline(std::cin, move);
                asio::write(socket, asio::buffer(move));
            }
            else if (server_msg.find("UPDATE_BOARD") != std::string::npos)
            {
                // Parse UPDATE_BOARD row,col,symbol
                int r, c;
                char s;
                sscanf(server_msg.c_str(), "UPDATE_BOARD %d,%d,%c", &r, &c, &s);
                board[r][c] = s;
                print_board();
            }
            else if (server_msg.find("INVALID_MOVE") != std::string::npos)
            {
                std::cout << "Invalid move! Try again.\n";
            }
            else if (server_msg.find("GAME_OVER") != std::string::npos)
            {
                print_board();
                if (server_msg.find("WIN") != std::string::npos)
                    std::cout << "You Win!\n";
                else if (server_msg.find("LOSE") != std::string::npos)
                    std::cout << "You Lose!\n";
                else
                    std::cout << "Draw!\n";
                break;
            }
        }
    }
    catch (std::exception &e)
    {
        std::cerr << "Exception: " << e.what() << "\n";
    }

    return 0;
}
