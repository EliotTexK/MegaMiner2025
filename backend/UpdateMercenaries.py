import math
from typing import List
from GameState import GameState
from Mercenary import Mercenary
from Demon import Demon
from PlayerBase import PlayerBase

def update_mercenaries(game_state: GameState):
    # Determine all merc states
    moving: List[Mercenary] = []
    fighting: List[Mercenary] = []
    waiting: List[Mercenary] = []
    set_all_merc_states(game_state, game_state.mercs, moving, fighting, waiting)

    # Move all mercs in moving state
    for merc in moving:
        move_merc_single(merc)

    # Apply combat effects for all mercs in fighting state
    for merc in fighting:
        do_merc_combat_single(merc)

    pass

# Side effect: All merc objects will have their state set appropiately
# Side effect: moving, fighting and waiting lists will be populated
def set_all_merc_states(game_state: GameState, mercs: List[Mercenary], 
                        moving: List[Mercenary],
                        fighting: List[Mercenary],
                        waiting: List[Mercenary]):
    for merc in mercs:
        next_tile1 = merc.get_adjacent_path_tile(game_state, 1)
        next_tile2 = merc.get_adjacent_path_tile(game_state, 2)
        blocking_entity1 = game_state.entity_grid[next_tile1[0], next_tile1[1]]
        blocking_entity2 = game_state.entity_grid[next_tile2[0], next_tile2[1]]

        # fighting if rival merc or demon or player base is within 2 spaces
        for ent in [blocking_entity1, blocking_entity2]:
            if (type(ent) == type(Demon) or 
                type(ent) == type(PlayerBase) or 
                (type(ent) == type(Mercenary) and ent.team != merc.team)):
                merc.state = 'fighting'
                # set all mercs behind us to waiting
                merc.set_behind_waiting(game_state)
            # if not waiting or fighting, then moving
            elif merc.state != 'waiting':
                merc.state = 'moving'
        
        # add to correct list
        if merc.state == 'fighting': fighting.append(merc)
        if merc.state == 'waiting': waiting.append(merc)
        if merc.state == 'moving': moving.append(merc)

def move_merc_single(merc: Mercenary):
    pass

def do_merc_combat_single(merc: Mercenary):
    pass