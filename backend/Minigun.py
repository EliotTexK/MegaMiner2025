import Constants
from Tower import Tower

class Minigun(Tower):
    def __init__(self, x: int, y: int, team_color: str) -> None:
        super().__init__(x, y, team_color, Constants.MINIGUN_MAX_COOLDOWN, Constants.MINIGUN_RANGE, Constants.MINIGUN_DAMAGE, Constants.MINIGUN_PRICE)

        self.name = select_tower_name('M',self.team)