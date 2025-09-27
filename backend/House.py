import Constants
from Tower import Tower

class House(Tower):
    def __init__(self, x: int, y: int, team_color: str) -> None:
        super().__init__(self, x, y, team_color, Constants.HOUSE_MAX_COOLDOWN)