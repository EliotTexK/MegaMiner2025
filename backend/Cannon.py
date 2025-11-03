import Constants
from Tower import Tower

class Cannon(Tower):
    def __init__(self, x: int, y: int, team_color: str) -> None:
        super().__init__(x , y, team_color, Constants.MINIGUN_MAX_COOLDOWN, Constants.MINIGUN_RANGE, Constants.MINIGUN_DAMAGE, Constants.MINIGUN_PRICE)

        self.radius = 2 # Cannon shots have a splash radius, this variable shows that
                        # But looking in the rules txt, cannon doesn't have this ability, so remove this? Discuss later
        
        self.name = select_tower_name('CA', self.team)