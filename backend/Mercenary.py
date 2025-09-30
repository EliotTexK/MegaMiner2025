import Constants
from GameState import GameState

class Mercenary:
    def __init__(self, x: int, y: int, team_color: str, state: str) -> None:
        self.hp = Constants.MERCENARY_INITIAL_HP
        self.x = x
        self.y = y
        self.state = state

        if team_color in ['r','b']:
            self.team = team_color
        else:
            raise Exception("Mercenary team_color must be 'r' or 'b'") # TF2 reference?
        
    # Helper function do find what path this merc is on. 
    # Side effect: passed list item 0 will be path coordinate list, item 1 will be position in list
    def get_current_path(self, game_state: GameState, data):
        current_path = []
        possible_paths = [game_state.mercenary_path_down, 
                    game_state.mercenary_path_left, game_state.mercenary_path_right,
                    game_state.mercenary_path_up]
    
        # Assumes no overlapping paths. If merc is on any path tile in path, we are on that path
        for path in possible_paths:
            if ([self.x, self.y] in path):
                current_path = path

        data[0] = current_path
        # position of merc along path (red to blue)
        data[1] = current_path.index([self.x, self.y])

    # Helper function that returns coordinates of the path tile forward or back from the merc's pos
    def get_adjacent_path_tile(self, game_state: GameState, delta: int):
        data = []
        self.get_current_path(game_state, data)
        path = data[0]
        path_pos = data[1]

        # if we are at the end of path, return last tile 
        # otherwise, return next tiles
        delta *= 1 if self.team == 'r' else -1
        return path[min(max(path_pos + delta, 0), len(path))]
    
    def set_behind_waiting(self, game_state: GameState):
        behind_pos = self.get_adjacent_path_tile(game_state, -1)
        behind_merc: Mercenary = game_state.entity_grid[behind_pos[0]][behind_pos[1]]
        # base case: we are in the first tile in our path, do not recurse
        if self.x == behind_pos[0] and self.y == behind_pos[1]:
            return
        else:
            behind_merc.state = 'waiting'
            behind_merc.set_behind_waiting(game_state)
