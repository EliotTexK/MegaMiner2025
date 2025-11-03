import Constants
from Tower import Tower
from GameState import GameState
from NameSelector import select_tower_name

class House(Tower):
    def __init__(self, x: int, y: int, team_color: str):
        super().__init__(x, y, team_color, Constants.HOUSE_MAX_COOLDOWN, Constants.HOUSE_RANGE, Constants.MINIGUN_DAMAGE, Constants.HOUSE_PRICE)

        self.money_gain = Constants.HOUSE_MONEY_PRODUCED
        self.angle = 0
        self.name = select_tower_name('H', self.team)
    
    def update(self, game_state):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
        else:
            self.tower_activation(game_state)
    
    def tower_activation(self, game_state : GameState):
        if self.team == "r":
            game_state.money_r += self.money_gain
        elif self.team == "b":
            game_state.money_b += self.money_gain