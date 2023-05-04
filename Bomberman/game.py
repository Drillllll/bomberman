from player import Player
import pygame
from enum import Enum
import random
import time


class Keys(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SPACE = 5

class BlockType(Enum):
    EMPTY = 1
    WALL = 2
    BLOWABLE = 3
    BOMB = 4

class GameState(Enum):
    WAITING = 1
    STARTED = 2
    ENDED = 3

class Game:
    def __init__(self, game_id):
        self.seconds_to_detonate = 3
        self.board_size = 20
        self.player_rect_size = 13
        self.bomb_rect_size = 6
        self.block_rect_size = 20
        self.game_state = GameState.WAITING
        self.game_id = game_id
        self.players = {}  # dictionary { player_number, player }
        # list of tuples (bomb_rect, i, time)
        # where i - index in board, position of block on which the bomb was planted
        # time - time of planting
        self.bombs = []
        self.player_colors = ((255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0))
        self.board = self.create_board()  # list of tuples (block_rect, block_type)


    def plant_bomb(self, player_rect):
        bomb_rect  = pygame.Rect(0, 0, self.bomb_rect_size, self.bomb_rect_size)
        index = 0
        current_time = time.time()

        # check in which board block the player_rect is located
        for i, (block_rect, block_type) in enumerate(self.board):
            if block_rect.colliderect(player_rect):
                # player_rect is contained within this block
                index = i  # return the index of the block in the board list
                bomb_rect.centerx = block_rect.centerx
                bomb_rect.centery = block_rect.centery

        self.bombs.append((bomb_rect, index, current_time))

    def destroy_surrounding_blocks(self, index):
        index_to_check = [index, index+1, index-1, index+self.board_size, index-self.board_size]
        for i in index_to_check:
            block = self.board[i]
            block_rect = block[0]
            type = block[1]
            if type == BlockType.BLOWABLE:
                self.board[i] = (block_rect, BlockType.EMPTY)

            for player_number, player in self.players.items():
                if block_rect.colliderect(player.rect):
                    player.isDead = True
            #players_to_remove = []
            #for player_number, player in self.players.items():
                #if block_rect.colliderect(player.rect):
                    #players_to_remove.append(player_number)
             #for player_number in players_to_remove:
             #del self.players[player_number]


    def check_if_ended(self):
        if self.game_state == GameState.WAITING:
            return
        alive_players = 0
        for player_number, player in self.players.items():
            if player.isDead is False:
                alive_players += 1
        if alive_players <= 1:
            self.game_state = GameState.ENDED

    def activate_bombs(self):
        current_time = time.time()
        for bomb in self.bombs:
            bomb_time = bomb[2]
            if current_time - bomb_time > self.seconds_to_detonate:
                self.destroy_surrounding_blocks(bomb[1])
                self.bombs.remove(bomb)

    def react_to_keys(self, keys, player_number):
        if self.game_state == GameState.WAITING or self.game_state == GameState.ENDED:
            return
        try:
            player_rect = self.players[player_number].rect
            player_rect_copy = player_rect.copy()

            if keys[Keys.LEFT]:
                player_rect_copy.x -= self.players[player_number].velocity
            if keys[Keys.RIGHT]:
                player_rect_copy.x += self.players[player_number].velocity
            if keys[Keys.UP]:
                player_rect_copy.y -= self.players[player_number].velocity
            if keys[Keys.DOWN]:
                player_rect_copy.y += self.players[player_number].velocity
            if keys[Keys.SPACE]:
                self.plant_bomb(player_rect)

            if (keys[Keys.LEFT] or keys[Keys.RIGHT] or keys[Keys.UP] or keys[Keys.DOWN]) is False:
                return

            collision = False

            # check collision with wall or blowable
            for block_rect, block_type in self.board:
                # Check if the block is a WALL or BLOWABLE block
                if block_type == BlockType.WALL or block_type == BlockType.BLOWABLE:
                    # Check if the player collides with the block
                    if player_rect_copy.colliderect(block_rect):
                        # Player cannot move
                        collision = True

            if collision is False:
                self.players[player_number].rect = player_rect_copy.copy()
        except:
            print("disconnected while reading keys")

    # returns important information to client to draw the game state
    def get_game_info(self):
        return self.board, self.players, self.bombs, self.game_state


    def add_player(self, player_number):
        player_rect = pygame.Rect(0, 0, self.player_rect_size, self.player_rect_size)

        # players stars in 4 corners
        if player_number == 0:
            index = self.board_size + 1
        if player_number == 1:
            index = 2 * self.board_size - 2
        if player_number == 2:
            index = self.board_size * (self.board_size - 2) + 1
        if player_number == 3:
            index = (self.board_size-1) * self.board_size - 2

        # center the player rectangle within the board box rectangle
        player_rect.centerx = self.board[index][0].centerx
        player_rect.centery = self.board[index][0].centery

        self.players[player_number] = Player(player_rect, self.player_colors[player_number], player_number)

    def create_board(self):
        pygame.init()
        board = self.randomize_board()  # board as a list of tuples

        # Set the first and last columns and rows to wall blocks
        for i in range(self.board_size):
            board[i] = (board[i][0], BlockType.WALL)
            board[(self.board_size - 1) * self.board_size + i] = (
            board[(self.board_size - 1) * self.board_size + i][0], BlockType.WALL)
            board[i * self.board_size] = (board[i * self.board_size][0], BlockType.WALL)
            board[(i + 1) * self.board_size - 1] = (board[(i + 1) * self.board_size - 1][0], BlockType.WALL)

        return board

    def randomize_board(self):
        # Define the possible block types and their probabilities
        block_types = [BlockType.EMPTY, BlockType.WALL, BlockType.BLOWABLE]
        block_probabilities = [0.6, 0.1, 0.3]

        # Create the board as a list of tuples
        # Create the board as a list of tuples
        board = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                # Create a Pygame rect object for the current rectangle
                block_rect = pygame.Rect(col * self.block_rect_size, row * self.block_rect_size, self.block_rect_size, self.block_rect_size)

                # keep corners empty
                if row in [0, 1, 2, self.board_size - 1, self.board_size - 2, self.board_size - 3] \
                        and col in [0, 1, 2, self.board_size - 1, self.board_size - 2, self.board_size - 3]:
                    block_type = BlockType.EMPTY
                else:
                    # Choose a random block type based on the defined probabilities
                    block_type = random.choices(block_types, block_probabilities)[0]

                # Add the current rectangle to the board list as a tuple of (rect, is_traversable, color)
                board.append((block_rect, block_type))

        return board
