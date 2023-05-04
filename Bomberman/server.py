import socket
from _thread import *
import threading
import pickle
from game import Game
from game import GameState

server = "192.168.1.17"
port = 5547
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP/IP socket
server_socket.bind((server, port)) # Bind the socket to a specific address and port
server_socket.listen(4)
print("Server started, waiting for clients")

connected_clients = []
games = {}  # empty dictionary - {game_id, game}
games_id_counter = 0

games_lock = threading.Lock()  # lock object protecting games dictionary


# for each client a new thread is started
def threaded_handle_client(client_socket, player_number, game_id):
    global games_id_counter
    # sending first response to client - his player number
    client_socket.send(pickle.dumps(player_number))
    with games_lock:
        games[game_id].add_player(player_number)

    # server - client communication loop
    while True:
        try:
            # receive pressed keys from client
            keys = pickle.loads(client_socket.recv(2048*2))
            with games_lock:
                games[game_id].react_to_keys(keys, player_number)
                games[game_id].activate_bombs()
                games[game_id].check_if_ended()

                if game_id in games:  # check if game is still present
                    game = games[game_id]
                    # send back the game information to draw the game state
                    client_socket.sendall(pickle.dumps(game.get_game_info()))
                else:
                    print("Game not present")
                    break
        except:
            print("communication problem")
            break

    print("Client disconnected")
    try:
        with games_lock:
            del games[game_id]  # deleting game
            print("Closing game, id: ", game_id)
    except:
        pass  # another player has already deleated the game
    games_id_counter -= 1
    client_socket.close()


while True:
    # accept() returns a new socket and the address of the client that has connected
    client_socket, client_address = server_socket.accept()
    print("New client, address: ", client_address)

    game_id = games_id_counter // 4  # for every 4 clients the game_id stays the same
    games_id_counter += 1

    if games_id_counter % 4 == 1:
        with games_lock:
            games[game_id] = Game(game_id)  # adding new entry to dictionary
            print("New game created, id: ", game_id)
    if games_id_counter % 4 == 0:
        with games_lock:
            games[game_id].game_state = GameState.STARTED
            print("4 players joined, game started, id: ", game_id)
            print(games[game_id].game_state)


    player_number = games_id_counter % 4
    # start new thread for every client
    start_new_thread(threaded_handle_client, (client_socket, player_number, game_id))
