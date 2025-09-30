from GameState import GameState
from Tower import Tower
from House import House
from Cannon import Cannon
from Minigun import Minigun
from Crossbow import Crossbow
from Constants import HOUSE_MAX_COOLDOWN, CANNON_MAX_COOLDOWN, MINIGUN_MAX_COOLDOWN, CROSSBOW_MAX_COOLDOWN

def update_towers(game_state: GameState):
    towers = game_state.towers

    # Iterates through the tower list, and lowers the cooldown for each appropriate type
    for tower in towers:
        current_cooldown = tower.current_cooldown
        current_team = tower.team_color

        ## House Tower activation
        if isinstance(tower, House):
            if current_cooldown > 0:
                current_cooldown -= 1
                if current_team == 'r':
                    game_state.money_r += 12
                else:
                    game_state.money_b += 12
            else:
                current_cooldown = HOUSE_MAX_COOLDOWN

        ## Cannon Tower activation
        if isinstance(tower, Cannon):
            if current_cooldown > 0:
                current_cooldown -= 1
                # Create projectile that damages enemy mercs
            else:
                current_cooldown = CANNON_MAX_COOLDOWN

        ## Minigun Tower activation
        if isinstance(tower, Minigun):
            if current_cooldown > 0:
                current_cooldown -= 1
                # Create projectile that damages enemy mercs
            else:
                current_cooldown = MINIGUN_MAX_COOLDOWN

        ## Crossbow Tower activation
        if isinstance(tower, Crossbow):
            if current_cooldown > 0:
                current_cooldown -= 1
                # Create projectile that damages enemy mercs
            else:
                current_cooldown = CROSSBOW_MAX_COOLDOWN