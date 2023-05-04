class Player:
    def __init__(self, rect, color, player_number):
        self.rect = rect
        self.color = color
        self.velocity = 3
        self.isDead = False
        self.player_number = player_number
