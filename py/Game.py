# import math
# import time
# import traceback
# import subprocess
# #import resource
# import sys
import json
#import copy
import GameObjects

class Game:
    def __init__(self, path1 = "", path2 = ""):
        self.AI_Path_1 : str = path1
        self.AI_Path_2 : str = path2

        self.state : GameObjects.GameState

    def reset():
        pass

    def run():
        pass

    def save_game_State_to_json(self) -> json:
        data = json.dump(self.state.map_tiles, 4)
        return data

    def load_game_state_from_json(self):
        pass

    def load_ai_paths(self, path_one : str, path_two : str):
        self.AI_Path_1 = path_one
        self.AI_Path_2 = path_two
    
    def can_build(self, x,  y, team_color):
        pass

    def can_destroy(self, x, y, team_color):
        pass

