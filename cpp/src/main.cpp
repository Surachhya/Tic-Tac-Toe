#include <iostream>
#include <string>
using namespace std;

int main() {
    cout << "Welcome to Tic Tac Toe!" << endl;
    cout << "Terminal UI coming soon... This is just for testing I will later use for tests" << endl;

    string name;
    cout << "Hi I am Tic Tac Toe. What is your name?" << endl;
    getline(cin, name);

    cout << "Hello, " << name << "! Ready to play?" << endl;

    cout << "Compile and run server.cpp and client.cpp to play actual the game." << endl;

    return 0;
}
