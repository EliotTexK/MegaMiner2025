import sys
import json
import string
import json

# Any imports from the standard library are allowed
import random

from typing import Optional
import json
import sys
import os

class AIAction:
    """
    Represents one turn of actions in the game.
    
    Phase 1 - Pick ONE:
        - Build a tower: AIAction("build", x, y, tower_type)
        - Destroy a tower: AIAction("destroy", x, y)
        - Do nothing: AIAction("nothing", 0, 0)
    
    Phase 2 - Optional:
        - Buy mercenary: add merc_direction="N" (or "S", "E", "W")
    
    Phase 3 - Optional:
        - Provoke Demons: add provoke_demons=True
        - To be used with caution!
    
    Possible values of tower_type are:
        - "crossbow"
        - "cannon"
        - "minigun"
        - "house"
        - "church"
    
    Examples:
        AIAction("build", 5, 3, "cannon")
        AIAction("build", 5, 3, "crossbow", merc_direction="N")
        AIAction("destroy", 2, 4)
        AIAction("nothing", 0, 0, merc_direction="S", provoke_demons=True)
    """
    
    def __init__(
        self,
        action: str,
        x: int,
        y: int,
        tower_type: str = "",
        merc_direction: str = "",
        provoke_demons: bool = False
    ):
        self.action = action.lower().strip()  # "build", "destroy", or "nothing"
        self.x = x
        self.y = y
        self.tower_type = tower_type.strip()
        self.merc_direction = merc_direction.upper().strip()  # "N", "S", "E", "W", or ""
        self.provoke_demons = provoke_demons
    
    def to_dict(self):
        """Convert to dictionary for saving/sending"""
        return {
            'action': self.action,
            'x': self.x,
            'y': self.y,
            'tower_type': self.tower_type,
            'merc_direction': self.merc_direction,
            'provoke_demons': self.provoke_demons
        }
    
    def to_json(self):
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


    # -- HELPER FUNCTIONS --
def is_out_of_bounds(game_state: dict, x: int, y: int) -> bool:
        return x < 0 or x >= len(game_state['FloorTiles'][0]) or y < 0 or y >= len(game_state['FloorTiles'])

    # team_color should be 'r' or 'b'
    # Return a list of strings representing available mercenary queue directions like: ["N","S","W"]
def get_available_queue_directions(game_state: dict, team_color: str) -> list:
        result = []

        offsets = {
            (0, -1): "N",
            (0, 1): "S",
            (1, 0): "E",
            (-1, 0): "W"
        }

        for offset in offsets.keys():
            player = game_state['PlayerBaseR'] if team_color == 'r' else game_state['PlayerBaseB']
            target_x = player['x'] + offset[0]
            target_y = player['y'] + offset[1]
            if (not is_out_of_bounds(game_state, target_x, target_y) and
                game_state['FloorTiles'][target_y][target_x] == "O"):
                result.append(offsets[offset])

        return result

    # team_color should be 'r' or 'b'
    # Return a list of coordinates that are available for building
def get_available_build_spaces(game_state: dict, team_color: str):
        result = []

        for y, row in enumerate(game_state['FloorTiles']):
            for x, chr_at_x in enumerate(row):
                if chr_at_x == team_color:
                    if game_state['EntityGrid'][y][x] == '':
                        result.append((x,y))

        return result

    # team_color should be 'r' or 'b'
    # Return a list of towers belonging to the selected team
def get_my_towers(game_state: dict, team_color: str):
        result = []

        for tower in game_state['Towers']:
            if tower["Team"] == team_color:
                result.append(tower)

        return result

    # team_color should be 'r' or 'b'
def get_my_money_amount(game_state: dict, team_color: str) -> int:
        return game_state["RedTeamMoney"] if team_color == 'r' else game_state["BlueTeamMoney"]

def lean(direction, build):
    space = build
    n = len(space)

    if direction == "left":
        for x in range(n):
            if random.randint(0, 100) < 40:
                return space[x]
    else:
        for x in range(n-1, -1, -1):
            if random.randint(0, 100) < 40:
                return space[x]
    return None

def find_map(direction, build, team):
    l = len(direction)
    size = len(build)

    #downloads_folder = os.path.expanduser("~/Downloads")
    #content = str(l)
    #content += "\n"
    #for x in direction:
    #    content += str(x)
    #    content += "\n"
    #content += str(team)
    #content += "\n"
    #content += str(size)
    #content += "\n"
    #create_txt_in_backend(downloads_folder, content)

    if team == 'r':
        if size == 28 and l == 3 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'E':
            return 0
        elif size == 21 and l == 4 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'E' and direction[3] == 'W':
            return 1
        elif size == 27 and l == 2 and direction[0] == 'N' and direction[1] == 'S':
            return 2
        elif size == 21 and l == 2 and direction[0] == 'S' and direction[1] == 'E':
            return 3
        elif size == 27 and l == 3 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'E':
            return 4
        elif size == 19 and l == 3 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'E':
            return 5
        elif size == 16 and l == 3 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'W':
            return 6
    else:
        if size == 28 and l == 3 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'W':
            return 0
        elif size == 21 and l == 4 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'E' and direction[3] == 'W':
            return 1
        elif size == 27 and l == 2 and direction[0] == 'N' and direction[1] == 'S':
            return 2
        elif size == 21 and l == 2 and direction[0] == 'S' and direction[1] == 'W':
            return 3
        elif size == 27 and l == 3 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'W':
            return 4
        elif size == 19 and l == 3 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'W':
            return 5
        elif size == 16 and l == 3 and direction[0] == 'N' and direction[1] == 'S' and direction[2] == 'E':
            return 6
    return -1

def find_best_direction(direction, map_get, team, turn, dir_get):
    #downloads_folder = os.path.expanduser("~/Downloads")
    #content = str(map_get)
    #content += "\n"
    #content += str(team)
    #content += "\n"
    #ontent += str(turn)
    #create_txt_in_backend(downloads_folder, content)
    if map_get == 0:
        if turn == 0:
            return 'W'
        elif turn == 1:
            return 'E'
        elif turn == 12:
            return 'N'
        elif turn == 13:
            return 'S'
        elif turn < 16:
            if team == 'r':
                return 'N'
            else:
                return 'S'
        else:
            directions = ['N', 'S', 'E', 'W']
            min_val = min(dir_get)  # find the minimum value
            # collect all indices that match the minimum
            candidates = [i for i, val in enumerate(dir_get) if val == min_val]
            # choose randomly among them
            chosen_index = random.choice(candidates)
            return directions[chosen_index]
    elif map_get == 1:
        if turn == 0:
            return 'W'
        if turn == 1:
            return 'E'
        if turn < 13:
            if team == 'r':
                return 'W'
            else:
                return 'E'
        else:
            directions = ['N', 'S', 'E', 'W']
            min_val = min(dir_get)  # find the minimum value
            # collect all indices that match the minimum
            candidates = [i for i, val in enumerate(dir_get) if val == min_val]
            # choose randomly among them
            chosen_index = random.choice(candidates)
            return directions[chosen_index]
    elif map_get == 2:
        if turn < 20:
            if team == 'r':
                return 'S'
            else:
                return 'N'
        directions = ['N', 'S', 'E', 'W']
        min_val = min(dir_get)  # find the minimum value
        # collect all indices that match the minimum
        candidates = [i for i, val in enumerate(dir_get) if val == min_val]
        # choose randomly among them
        chosen_index = random.choice(candidates)
        return directions[chosen_index]
    elif map_get == 3:
        if turn < 20:
            if team == 'r':
                return 'E'
            else:
                return 'W'
        directions = ['N', 'S', 'E', 'W']
        min_val = min(dir_get)  # find the minimum value
        # collect all indices that match the minimum
        candidates = [i for i, val in enumerate(dir_get) if val == min_val]
        # choose randomly among them
        chosen_index = random.choice(candidates)
        return directions[chosen_index]
    elif map_get == 4:
        if turn < 20:
            if team == 'r':
                if random.randint(1, 2) < 2:
                    return 'N'
                else:
                    return 'E'
            directions = ['N', 'S', 'E', 'W']
            min_val = min(dir_get)  # find the minimum value
            # collect all indices that match the minimum
            candidates = [i for i, val in enumerate(dir_get) if val == min_val]
            # choose randomly among them
            chosen_index = random.choice(candidates)
            return directions[chosen_index]
    elif map_get == 5:
        if turn < 20:
            if team == 'r':
                return 'N'
            else:
                return 'S'
        if random.randint(1, 100) < 10:
            return 'N'
        directions = ['N', 'S', 'E', 'W']
        min_val = min(dir_get)  # find the minimum value
        # collect all indices that match the minimum
        candidates = [i for i, val in enumerate(dir_get) if val == min_val]
        # choose randomly among them
        chosen_index = random.choice(candidates)
        return directions[chosen_index]
    elif map_get == 6:
        if turn == 0 or turn == 1:
            return 'S'
        if turn < 13:
            if team == 'r':
                return 'W'
            else:
                return 'E'
        else:
            directions = ['N', 'S', 'E', 'W']
            min_val = min(dir_get)  # find the minimum value
            # collect all indices that match the minimum
            candidates = [i for i, val in enumerate(dir_get) if val == min_val]
            # choose randomly among them
            chosen_index = random.choice(candidates)
            return directions[chosen_index]
    return random.choice(direction)

def find_backend_folder(downloads_path):
    for root, dirs, files in os.walk(downloads_path):
        if 'AI_Agents' in dirs:
            return os.path.join(root, 'AI_Agents')
    return None

def create_txt_in_backend(downloads_path, content, filename="logger.txt"):
    backend_path = find_backend_folder(downloads_path)
    if backend_path:
        file_path = os.path.join(backend_path, filename)
        with open(file_path, "w") as f:
            f.write(content)

def search_log_for_keyword(downloads_path, keyword):
    for root, dirs, files in os.walk(downloads_path):
        if "log.txt" in files:
            log_path = os.path.join(root, "log.txt")
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if keyword in line:
                            return True
            except Exception as e:
                print(f"Error reading {log_path}: {e}")
    return False

class Agent:
    def initialize_and_set_name(self, initial_game_state: dict, team_color: str) -> str:
        # -- YOUR CODE BEGINS HERE --
        # Competitors: Do any initialization here

        # It's essential that you keep track of which team you're on
        self.team_color = team_color

        self.num_houses = 0
        self.num_cannons = 0
        self.num_crossbows = 0
        self.num_miniguns = 0
        self.map_at = -2
        self.dir_full = [0, 0, 0, 0]

        # Return a string representing your team's name
        return "Ultimate Overtake"
        # -- YOUR CODE ENDS HERE --
    
    # Take in a dictionary representing the game state, then output an AI Action
    def do_turn(self, game_state: dict) -> AIAction:
        # Competitors: For your convenience, it's recommended that you use the helper functions given earlier in this file
        q_directions = get_available_queue_directions(game_state, self.team_color)
        build_spaces = get_available_build_spaces(game_state, self.team_color)
        my_money = get_my_money_amount(game_state, self.team_color)
        my_towers = get_my_towers(game_state, self.team_color)

        turn = game_state["CurrentTurn"]

        if turn == 0:
            self.map_at = find_map(q_directions, build_spaces, self.team_color)


        if self.map_at == 0:
            if team_color == 'r':
                self.dir_full[3] = 1000
            elif team_color == 'b':
                self.dir_full[2] = 1000
        elif self.map_at == 2:
            self.dir_full[2] = 1000
            self.dir_full[3] = 1000
        elif self.map_at == 3:
            self.dir_full[0] = 1000
            if team_color == 'r':
                self.dir_full[3] = 1000
            elif team_color == 'b':
                self.dir_full[2] = 1000
        elif self.map_at == 4:
            if team_color == 'r':
                self.dir_full[3] = 1000
            elif team_color == 'b':
                self.dir_full[2] = 1000
        elif self.map_at == 5:
            if team_color == 'r':
                self.dir_full[3] = 1000
            elif team_color == 'b':
                self.dir_full[2] = 1000
        elif self.map_at == 6:
            if team_color == 'r':
                self.dir_full[2] = 1000
            elif team_color == 'b':
                self.dir_full[3] = 1000

        #downloads_folder = os.path.expanduser("~/Downloads")
        #content = str(map_at)
        #create_txt_in_backend(downloads_folder, content)

        # The game is taking too long! Give up at turn 50
        #if turn >= 50 and len(my_towers) > 0:
        #    to_destroy = random.choice(my_towers)
        #    return AIAction("destroy", to_destroy["x"], to_destroy["y"])

        do_provoke = False
        # If everybody uses this agent, there will be a nice reset on turn 38
        # do_provoke = (turn == 30 and self.team_color == 'r') or (turn == 31 and self.team_color == 'b') or (turn == 38)

        # Push towards heavy house building first 12 moves
        if (turn == 0 and team_color == 'b') or (turn == 1 and team_color == 'r'):
            chr = find_best_direction(q_directions, self.map_at, team_color, turn, self.dir_full)
            if chr == 'N':
                self.dir_full[0] += 1
            elif chr == 'S':
                self.dir_full[1] += 1
            elif chr == 'E':
                self.dir_full[2] += 1
            elif chr == 'W':
                self.dir_full[3] += 1
            return AIAction("nothing", 0, 0, merc_direction=chr, provoke_demons=do_provoke)
        if (turn == 12 and team_color == 'b') or (turn == 11 and team_color == 'r'):
            chr = find_best_direction(q_directions, self.map_at, team_color, turn, self.dir_full)
            if chr == 'N':
                self.dir_full[0] += 1
            elif chr == 'S':
                self.dir_full[1] += 1
            elif chr == 'E':
                self.dir_full[2] += 1
            elif chr == 'W':
                self.dir_full[3] += 1
            return AIAction("nothing", 0, 0, merc_direction=chr, provoke_demons=do_provoke)
        elif turn < 16:
            if team_color == 'r':
                ans = lean("left", build_spaces)
            else:
                ans = lean("right", build_spaces)

            if ans is None:
                house_x, house_y = random.choice(build_spaces)
            else:
                house_x = ans[0]
                house_y = ans[1]
            self.num_houses += 1
            return AIAction("build", house_x, house_y, 'house', provoke_demons=do_provoke)
        else:

            if len(build_spaces) > 0 and random.randint(1, 100) < 12-int(turn/10):
                if team_color == 'r':
                    ans = lean("left", build_spaces)
                else:
                    ans = lean("right", build_spaces)

                if ans is None:
                    house_x, house_y = random.choice(build_spaces)
                else:
                    house_x = ans[0]
                    house_y = ans[1]
                return AIAction("build", house_x, house_y, 'house', provoke_demons=do_provoke)
            elif len(build_spaces) > 0 and random.randint(1, 100) < 20+int(turn/10):
                tower_choices = [
                    'minigun',
                    'church',
                ]
                if team_color == 'r':
                    ans_next = lean("right", build_spaces)
                else:
                    ans_next = lean("left", build_spaces)

                if ans_next is None:
                    tower_x, tower_y = random.choice(build_spaces)
                else:
                    tower_x = ans_next[0]
                    tower_y = ans_next[1]

                if random.randint(1, 100) < 100-turn:
                    tower = tower_choices[0]
                else:
                    tower = tower_choices[1]

                chr = find_best_direction(q_directions, self.map_at, team_color, turn, self.dir_full)
                return AIAction("build", tower_x, tower_y, tower, merc_direction=chr, provoke_demons=do_provoke)
            else:
                chr = find_best_direction(q_directions, self.map_at, team_color, turn, self.dir_full)
                """downloads_folder = os.path.expanduser("~/Downloads")
                content = str(chr)
                content += "\n"
                content += "\n"
                for x in self.dir_full:
                content += str(x)
                content += "\n"
                create_txt_in_backend(downloads_folder, content)"""
                
                if self.map_at == 5 and random.randint(1, 100) < 22:
                    if team_color == 'r':
                        chr = 'N'
                        self.dir_full[0] -= 1
                    elif team_color == 'b':
                        chr = 'S'
                        self.dir_full[1] -= 1
                if self.map_at == 5 and random.randint(1, 100) < 5:
                    if team_color == 'r':
                        chr = 'E'
                        self.dir_full[2] -= 1
                    elif team_color == 'b':
                        chr = 'W'
                        self.dir_full[3] -= 1


                if chr == 'N':
                    self.dir_full[0] += 1
                elif chr == 'S':
                    self.dir_full[1] += 1
                elif chr == 'E':
                    self.dir_full[2] += 1
                elif chr == 'W':
                    self.dir_full[3] += 1
                else:
                    downloads_folder = os.path.expanduser("~/Downloads")
                    content = str(chr)
                    content += "\n"
                    content += "\n"
                    for x in self.dir_full:
                        content += str(x)
                        content += "\n"
                    create_txt_in_backend(downloads_folder, content)
                return AIAction("nothing", 0, 0, merc_direction=chr, provoke_demons=do_provoke)


# -- DRIVER CODE (LEAVE THIS AS-IS) --
# Competititors: Altering code below this line will result in disqualification!
if __name__ == '__main__':

    # figure out if we're red or blue
    team_color = 'r' if input() == "--YOU ARE RED--" else 'b'

    # get initial game state
    input_buffer = [input()]
    while input_buffer[-1] != "--END INITIAL GAME STATE--":
        input_buffer.append(input())
    game_state_init = json.loads(''.join(input_buffer[:-1]))

    # create and initialize agent, set team name
    agent = Agent()
    print(agent.initialize_and_set_name(game_state_init, team_color))

    # perform first action
    print(agent.do_turn(game_state_init).to_json())

    # loop until the game is over
    while True:
        # get this turn's state
        input_buffer = [input()]
        while input_buffer[-1] != "--END OF TURN--":
            input_buffer.append(input())
        game_state_this_turn = json.loads(''.join(input_buffer[:-1]))

        # get agent action, then send it to the game server
        print(agent.do_turn(game_state_this_turn).to_json())