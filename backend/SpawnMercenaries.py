from GameState import GameState
from Mercenary import Mercenary

def spawn_mercenaries(game_state: GameState):

    bx = game_state.player_base_r.x
    by = game_state.player_base_r.y

    if game_state.player_base_r.mercenary_queued_up > 0 and game_state.entity_grid[by - 2][bx]:
        game_state.entity_grid[by - 2][bx] = Mercenary(bx, by, "r", "blah")

    if game_state.player_base_r.mercenary_queued_down > 0 and game_state.entity_grid[by + 2][bx]:
        game_state.entity_grid[by + 2][bx] = Mercenary(bx, by, "r", "blee")

    if game_state.player_base_r.mercenary_queued_left > 0 and game_state.entity_grid[by][bx - 2]:
        game_state.entity_grid[by][bx - 2] = Mercenary(bx - 2, by, "r", "blue")

    if game_state.player_base_r.mercenary_queued_right > 0 and game_state.entity_grid[by][bx + 2]:
        game_state.entity_grid[by][bx + 2] = Mercenary(bx + 2, by, "r", "balanced")

    bx = game_state.player_base_b.x
    by = game_state.player_base_b.y
    
    if game_state.player_base_b.mercenary_queued_up > 0 and game_state.entity_grid[by - 2][bx] == None:

        game_state.entity_grid[by - 2][bx] = Mercenary(bx, by - 2, "b", "blah blah why is this in the constructor")
        game_state.mercs.append(game_state.entity_grid[by - 2][bx])
        game_state.player_base_b.mercenary_queued_up -= 1
        

    if game_state.player_base_b.mercenary_queued_down > 0 and game_state.entity_grid[by + 2][bx]:
        game_state.entity_grid[by + 2][bx] = Mercenary(bx, by, "b", "hello")

    if game_state.player_base_b.mercenary_queued_left > 0 and game_state.entity_grid[by][bx - 2]:
        game_state.entity_grid[by][bx - 2] = Mercenary(bx, by, "b", "hello")

    if game_state.player_base_b.mercenary_queued_right > 0 and game_state.entity_grid[by][bx + 2]:
        game_state.entity_grid[by][bx + 2] = Mercenary(bx, by, "b", "hey guys")


    