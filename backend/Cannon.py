import Constants
from Tower import Tower

class Cannon(Tower):
    def __init__(self, x: int, y: int, team_color: str) -> None:
        super().__init__(self, x, y, team_color, Constants.CANNON_MAX_COOLDOWN)