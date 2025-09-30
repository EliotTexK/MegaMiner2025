# Phase 3 | Updates everything, making things move/attack and determining win/lose

from GameState import GameState
from UpdateMercenaries import update_mercenaries
from UpdateDemons import update_demons
from SpawnMercenaries import spawn_mercenaries
from SpawnDemons import spawn_demons
from PlayerBase import PlayerBase

def world_update_phase(game_state: GameState):
    update_mercenaries(game_state)
    check_wincon(game_state)

    update_demons(game_state)
    check_wincon(game_state)
    
    spawn_mercenaries(game_state)
    spawn_demons(game_state)

def check_wincon(game_state: GameState):
    team_b_hp = game_state.player_base_b.hp
    team_r_hp = game_state.player_base_r.hp

    if team_b_hp <= 0 or team_r_hp <= 0:
        if team_b_hp == 0:
            pass
            # Team R is the winner!
        elif team_r_hp == 0:
            pass
            # Team B is the winner!
    if team_b_hp <= 0 and team_r_hp <= 0:
        pass
    else:
        pass
        # Nobody has won yet

##A player base is Destroyed if it has zero or less HP.

##If one player's base is Destroyed and the other is not, the player with the surviving base wins.

##If both players' bases are Destroyed, break the tie based on who has the most Gold.

##Then, if both players have the same amount of Gold, break the tie based on who has built the most towers.

##Then, if both players have built the same number of towers, break the tie based on the sum of prices of those towers.

##Then, if both sums are equal, break the tie based on the number of Mercenaries each player has.

##Then, if both have the same number of Mercenaries, break the tie based on the sum of HP of mercenaries.

    pass # TODO