import pygame
from network import Network
from game import BlockType
from game import Keys
from game import GameState
import traceback # errors

screen_width = 500
screen_height = 500
window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bomber")
pygame.font.init()
font = pygame.font.Font(None, 36)


def draw_window(game_info, player_number):
    board = game_info[0]
    players = game_info[1]
    bombs = game_info[2]
    # list of tuples (bomb_rect, i, time)
    # where i - index in board, position of block on which the bomb was planted
    game_state = game_info[3]

    # show the game state
    if game_state == GameState.WAITING:
        str = "Waiting for players"
    if game_state == GameState.STARTED:
        str = "Game started"
    if game_state == GameState.ENDED:
        str = "Game ended"
    window.fill((0, 0, 0))
    game_state_text = font.render(str, True, (255, 255, 255))
    window.blit(game_state_text, (80, 425))

    # show the winner
    if game_state == GameState.ENDED:
        winner_color = (0, 0, 0)
        for player_id, player in players.items():
            if player.isDead is False:
                winner_color = player.color
        pygame.draw.rect(window, winner_color, (100, 460, 20, 20))
        winner_text = font.render("Won", True, (255, 255, 255))
        window.blit(winner_text, (130, 460))

    # Draw the board
    for block_rect, block_type in board:
        # Determine the color of the block based on its type
        if block_type == BlockType.EMPTY:
            color = (255, 255, 255)  # white
        elif block_type == BlockType.WALL:
            color = (25, 25, 25)  # grey
        else:
            color = (75, 32, 0)

        # Draw the block
        pygame.draw.rect(window, color, block_rect)

    # Draw the players
    for player_id, player in players.items():
        if player.isDead is False:
            pygame.draw.rect(window, player.color, player.rect)

    # Draw the bombs
    for i in range(len(bombs)):
        pygame.draw.rect(window,(255, 165, 0), bombs[i][0] )

    pygame.display.flip()



def get_keys_pressed():
    keys = {}  # dictionary (Keys.key, isClicked)
    pygame_keys = pygame.key.get_pressed()
    keys[Keys.LEFT] = False
    keys[Keys.RIGHT] = False
    keys[Keys.UP] = False
    keys[Keys.DOWN] = False
    keys[Keys.SPACE] = False

    if pygame_keys[pygame.K_LEFT]:
        keys[Keys.LEFT] = True
    if pygame_keys[pygame.K_RIGHT]:
        keys[Keys.RIGHT] = True
    if pygame_keys[pygame.K_UP]:
        keys[Keys.UP] = True
    if pygame_keys[pygame.K_DOWN]:
        keys[Keys.DOWN] = True
    if pygame_keys[pygame.K_SPACE]:
        keys[Keys.SPACE] = True
    return keys

def run_game():
    clock = pygame.time.Clock()  # to maintain fps
    network = Network()  # create Network object to communicate with the sever
    player_number = network.connect()


    # game loop
    game_running = True
    while game_running:
        # stop the game loop for the amount of time necessary to
        # maintain a frame rate of 60 frames per second
        clock.tick(60)
        keys = get_keys_pressed()


        # client - server communication
        try:
             # sending and receiving
            game_info = network.send(keys)  # send keys pressed, receive game info
        except:
            game_running = False
            print("Error: client-server communication")
            break

        # quiting game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                pygame.quit()
                break

        try:
            draw_window(game_info, player_number)
        except:
            print("drawing problem, disconnected")


run_game()
