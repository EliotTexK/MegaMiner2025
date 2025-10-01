import Constants
import math
from PlayerBase import PlayerBase
from PIL import Image
import numpy as np

class GameState:
    ## Does game state need team_color?
    def __init__(self, team_color: str, map_width: int, map_height: int) -> None:
        self.turns_progressed = 999
        self.victory = None
        self.team_name_r = None
        self.team_name_b = None
        self.money_r = Constants.INITIAL_MONEY
        self.money_b = Constants.INITIAL_MONEY

        # Map specifications
        self.map_width = map_width
        self.map_height = map_height
        
        self.tile_grid = self.make_tile_grid_from_image() # 2d array of strings
        # TODO: this should come from parameters to this contructor function
        self.entity_grid = [ [0 for i in range(map_height)] , [0 for i in range(map_width)]]
        

        # TODO: this should come from parameters to this constructor function
        self.player_base_r : PlayerBase = PlayerBase(0,0,"r") # call PlayerBase() to define more, PlayerBase.py still needs updated
        self.player_base_b : PlayerBase = PlayerBase(0,1,"b") # call PlayerBase() to define more, PlayerBase.py still needs updated

        # Arrays that will hold the active entities for each type
        self.mercs = []
        self.towers = []
        self.demons = []
        self.demon_spawners = []

        # Compute mercenary paths, from Red to Blue player bases
        self.mercenary_path_left  = self.compute_mercenary_path((self.player_base_r.x-1, self.player_base_r.y))
        self.mercenary_path_right = self.compute_mercenary_path((self.player_base_r.x+1, self.player_base_r.y))
        self.mercenary_path_up    = self.compute_mercenary_path((self.player_base_r.x, self.player_base_r.y-1))
        self.mercenary_path_down  = self.compute_mercenary_path((self.player_base_r.x, self.player_base_r.y+1))

    ##Uses RGB values to construct a map, full red is red terratoy, full blue is blue terrarort, full green is path, black is void
    ##using r, b, and # == path, _ = void
    def make_tile_grid_from_image(self):
        map_image_path = "backend/maps/map.png"
        image = Image.open(map_image_path)
        pix_arry = np.asarray(image)
        tile_grid = []
        for x in range(len(pix_arry)):
            row = []
            for y in range(len(pix_arry[x])):
                if pix_arry[x][y][0] == 255 and pix_arry[x][y][1] == 0 and pix_arry[x][y][2] == 0:
                    row.append('r')
                elif pix_arry[x][y][0] == 0 and pix_arry[x][y][1] == 255 and pix_arry[x][y][2] == 0:
                    row.append('b')
                elif pix_arry[x][y][0] == 0 and pix_arry[x][y][1] == 0 and pix_arry[x][y][2] == 255:
                    row.append('Path') ## I see that we're using path in compute_merc(), so Ill make it path on the grid
                elif pix_arry[x][y][0] == 0 and pix_arry[x][y][1] == 0 and pix_arry[x][y][2] == 0:
                    row.append('_')
            tile_grid.append(row)

        print(tile_grid)
        return tile_grid
    
    def compute_mercenary_path(self, start_point: tuple) -> list:
        # See if there's a path starting at the starting point
        if self.tile_grid[start_point[0]][start_point[1]] == 'Path':
            # Do bastard DFS algorithm: raise exception if there's any branch in the path
            computed_path = [start_point]
            current_tile = start_point
            traversed = set()
            traversed.add(start_point)

            # Loop through new neighboring tiles until there are none left or a branch is detected
            while current_tile != None:
                # Find the next tile in the path
                for neighbor in [
                    (current_tile.x - 1, current_tile.y)
                    (current_tile.x + 1, current_tile.y)
                    (current_tile.x, current_tile.y - 1)
                    (current_tile.x, current_tile.y + 1)
                ]:
                    current_tile = None
                    if neighbor not in traversed and self.tile_grid[neighbor.x][neighbor.y] == 'Path':
                        traversed.add(neighbor)
                        if current_tile == None: current_tile = neighbor
                        else: raise Exception('Branching detected in mercenary path')
                
                # Record the next tile
                computed_path.append(current_tile) 
        else:
            return None
