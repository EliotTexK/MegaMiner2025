import sys
import json
import string
import json

from operator import itemgetter

# Any imports from the standard library are allowed
import random

from typing import Optional
import json

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

def get_roads_in_range(game_state: dict, tower_tile: tuple, tower_range: int):
    #euclidian distance algorithm
    count = 0
    tx = tower_tile[0]
    ty = tower_tile[1]
    for y, row in enumerate(game_state['FloorTiles']):
        for x, tile in enumerate(row):
            dx = x - tx
            dy = y - ty
            if(tile == 'O'):
                if(dx*dx + dy*dy <= tower_range * tower_range):
                    count += 1
    return count

def rate_build_tile(game_state: dict, tile_x: int, tile_y: int, tower_stats: tuple):
    damage = tower_stats[3]
    cooldown = tower_stats[1]
    tower_range = tower_stats[2]
    coord_tuple = (tile_x, tile_y)
    roads = get_roads_in_range(game_state, coord_tuple, tower_range)
    if tower_stats[3] != 5:
        score = (roads * damage) / cooldown
    else:
        score = ((1.5*roads) * damage) / cooldown
    return score

def rate_house_tile(game_state: dict, tile_x: int, tile_y: int, house_stats: tuple):
    coord_tuple = (tile_x, tile_y)
    roads = get_roads_in_range(game_state, coord_tuple, 5)
    score = roads
    return score


# -- AGENT CLASS (COMPETITORS WILL IMPLEMENT THIS) --
class Agent:
    def initialize_and_set_name(self, initial_game_state: dict, team_color: str) -> str:
        # -- YOUR CODE BEGINS HERE --
        # Competitors: Do any initialization here
        self.num_houses = 0
        self.num_mercenaries = 0
        self.num_cannons = 0
        self.num_miniguns = 0
        self.num_crossbows = 0
        self.num_churches = 0

        merc_price = 10

        base_house_price = 10
        base_house_cooldown = 5
        base_house_production = 12

        base_church_price = 15
        base_church_cooldown = 10
        base_church_range = 3

        base_cannon_price = 10
        base_cannon_cooldown = 5
        base_cannon_range = 3
        base_cannon_damage = 5

        base_minigun_price = 20
        base_minigun_cooldown = 1
        base_minigun_range = 3
        base_minigun_damage = 2

        base_crossbow_price = 8
        base_crossbow_cooldown = 4
        base_crossbow_range = 5
        base_crossbow_damage = 3

        self.house_tuple = (base_house_price, base_house_cooldown)
        self.cannon_tuple = (base_cannon_price, base_cannon_cooldown, base_cannon_range, base_cannon_damage)
        self.minigun_tuple = (base_minigun_price, base_minigun_cooldown, base_minigun_range, base_minigun_damage)
        self.crossbow_tuple = (base_crossbow_price, base_crossbow_cooldown, base_crossbow_range, base_crossbow_damage)
        self.church_tuple = (base_church_price, base_church_cooldown, base_church_range)

        self.merc_north_count = 0
        self.merc_south_count = 0
        self.merc_east_count = 0
        self.merc_west_count = 0

        # It's essential that you keep track of which team you're on
        self.team_color = team_color

        # Return a string representing your team's name
        return "Team5"
        # -- YOUR CODE ENDS HERE --
    
    # Take in a dictionary representing the game state, then output an AI Action
    def do_turn(self, game_state: dict) -> AIAction:
        # -- YOUR CODE BEGINS HERE --
        #Implement loop that reads location of all of our tiles into an array
        build_spaces = get_available_build_spaces(game_state, self.team_color)
        my_cash = get_my_money_amount(game_state, self.team_color)
        num_towers = self.num_cannons + self.num_crossbows + self.num_miniguns

        friendly_merc_count = 0
        enemy_merc_count = 0
        bad_demon_count = 0
        for item in game_state["Mercenaries"]:
            if item["Team"] == self.team_color:
                friendly_merc_count += 1
            elif item["Team"] != self.team_color:
                enemy_merc_count += 1
        for item in game_state["Demons"]:
            if item["Team"] == self.team_color:
                bad_demon_count += 1

        turn = game_state["CurrentTurn"]

        #cannon_score = [(temp_x, temp_y, 10)]
        cannon_score = []
        for i in build_spaces:
            temp_x, temp_y = i
            score = rate_build_tile(game_state, temp_x, temp_y, self.cannon_tuple)
            cannon_score.append((temp_x, temp_y, score))
        #crossbow_score = [(temp_x, temp_y, 12)]
        crossbow_score = []
        for i in build_spaces:
            temp_x, temp_y = i
            score = rate_build_tile(game_state, temp_x, temp_y, self.crossbow_tuple)
            crossbow_score.append((temp_x, temp_y, score))
        #minigun_score  = [(temp_x, temp_y, 13)]
        minigun_score = []
        for i in build_spaces:
            temp_x, temp_y = i
            score = rate_build_tile(game_state, temp_x, temp_y, self.minigun_tuple)
            minigun_score.append((temp_x, temp_y, score))

        house_score = []
        for i in build_spaces:
            temp_x, temp_y = i
            score = rate_house_tile(game_state, temp_x, temp_y, self.house_tuple)
            house_score.append((temp_x, temp_y, score))

        church_score = []
        for i in build_spaces:
            temp_x, temp_y = i
            score = rate_house_tile(game_state, temp_x, temp_y, self.church_tuple)
            church_score.append((temp_x, temp_y, score))
    
        if 2 <= turn <= 5:
            return AIAction("nothing",0,0)
        
        elif turn == 0 or turn == 1 or turn == 8 or turn == 15:
            house_min = min(house_score, key=itemgetter(2))
            self.num_houses += 1
            return AIAction("build", house_min[0], house_min[1], "house")
        
        elif 8 < turn < 11:
            return AIAction("nothing",0,0)
        
        elif turn == 13 or turn == 14:
            return AIAction("nothing",0,0)

        elif turn == 6 or turn == 12:
            merc_directions = get_available_queue_directions(game_state, self.team_color)
            rand_int = random.randint(0, len(merc_directions)-1)
            return AIAction("nothing",0,0,merc_direction=merc_directions[rand_int])
        
        elif turn >= 17 and turn % 2 == 0 and self.num_churches < 2:
            church_max = max(church_score, key=itemgetter(2))
            self.num_churches += 1
            return AIAction("build", church_max[0], church_max[1], "church")
        
        elif turn >= 50 and turn % 20 == 0 and len(build_spaces) > 7:
            house_min = min(house_score, key=itemgetter(2))
            self.num_houses += 1
            return AIAction("build", house_min[0], house_min[1], "house")
        
        elif 16 <= turn < 50 or turn > 50:
            cannon_max = max(cannon_score, key=itemgetter(2))
            crossbow_max = max(crossbow_score, key=itemgetter(2))
            minigun_max = max(minigun_score, key=itemgetter(2))
            house_min = min(house_score, key=itemgetter(2))

            rand_num = random.randint(0, 2)
            prov_chance = random.randint(0, 8)

           #if (num_towers / self.num_houses) <= 3/2 and num_towers >= 1:
            if rand_num == 0:
                if cannon_max[2] >= crossbow_max[2] and cannon_max[2] >= minigun_max[2]:
                    if (my_cash - self.cannon_tuple[0]) >= 0:
                        self.num_cannons += 1
                    if (prov_chance == 0):
                        return AIAction("build", cannon_max[0], cannon_max[1], "cannon", provoke_demons=True)
                    else:
                        return AIAction("build", cannon_max[0], cannon_max[1], "cannon")
                elif crossbow_max[2] >= minigun_max[2] and crossbow_max[2] >= cannon_max[2]:
                    if (my_cash - self.crossbow_tuple[0]) >= 0:
                        self.num_crossbows += 1
                    if (prov_chance == 0):
                        return AIAction("build", crossbow_max[0], crossbow_max[1], "crossbow", provoke_demons=True)
                    else:
                        return AIAction("build", crossbow_max[0], crossbow_max[1], "crossbow")
                elif minigun_max[2] >= crossbow_max[2] and minigun_max[2] >= cannon_max[2]:
                    if (my_cash - self.minigun_tuple[0]) >= 0:
                        self.num_miniguns += 1
                    if (prov_chance == 0):
                        return AIAction("build", minigun_max[0], minigun_max[1], "minigun", provoke_demons=True)
                    else:
                        return AIAction("build", minigun_max[0], minigun_max[1], "minigun")
                
            #elif num_towers < 1:
            elif rand_num == 1:
                merc_directions = get_available_queue_directions(game_state, self.team_color)
                direction_counts = []
                for direction in merc_directions:
                    if direction == "N":
                        direction_counts.append(self.merc_north_count)
                    elif direction == "S":
                        direction_counts.append(self.merc_south_count)
                    elif direction == "E":
                        direction_counts.append(self.merc_east_count)
                    elif direction == "W":
                        direction_counts.append(self.merc_west_count)
                
                next_merc_direction = merc_directions[direction_counts.index(min(direction_counts))]

                if cannon_max[2] >= crossbow_max[2] and cannon_max[2] >= minigun_max[2]:
                    if (my_cash - self.cannon_tuple[0]) >= 0:
                        self.num_cannons += 1
                    if (prov_chance == 0):
                        if (next_merc_direction == "N" and my_cash - 10 >= 0):
                            self.merc_north_count += 1
                        elif (next_merc_direction == "S" and my_cash - 10 >= 0):
                            self.merc_south_count += 1
                        elif (next_merc_direction == "E" and my_cash - 10 >= 0):
                            self.merc_east_count += 1
                        elif (next_merc_direction == "W" and my_cash - 10 >= 0):
                            self.merc_west_count += 1
                        return AIAction("build", cannon_max[0], cannon_max[1], "cannon", merc_direction=next_merc_direction, provoke_demons=True)
                    else:
                        if (next_merc_direction == "N" and my_cash - 10 >= 0):
                            self.merc_north_count += 1
                        elif (next_merc_direction == "S" and my_cash - 10 >= 0):
                            self.merc_south_count += 1
                        elif (next_merc_direction == "E" and my_cash - 10 >= 0):
                            self.merc_east_count += 1
                        elif (next_merc_direction == "W" and my_cash - 10 >= 0):
                            self.merc_west_count += 1
                        return AIAction("build", cannon_max[0], cannon_max[1], "cannon", merc_direction=next_merc_direction)
                elif crossbow_max[2] >= minigun_max[2] and crossbow_max[2] >= cannon_max[2]:
                    if (my_cash - self.crossbow_tuple[0]) >= 0:
                        self.num_crossbows += 1
                    if (prov_chance == 0):
                        if (next_merc_direction == "N" and my_cash - 10 >= 0):
                            self.merc_north_count += 1
                        elif (next_merc_direction == "S" and my_cash - 10 >= 0):
                            self.merc_south_count += 1
                        elif (next_merc_direction == "E" and my_cash - 10 >= 0):
                            self.merc_east_count += 1
                        elif (next_merc_direction == "W" and my_cash - 10 >= 0):
                            self.merc_west_count += 1
                        return AIAction("build", crossbow_max[0], crossbow_max[1], "crossbow", merc_direction=next_merc_direction, provoke_demons=True)
                    else:
                        if (next_merc_direction == "N" and my_cash - 10 >= 0):
                            self.merc_north_count += 1
                        elif (next_merc_direction == "S" and my_cash - 10 >= 0):
                            self.merc_south_count += 1
                        elif (next_merc_direction == "E" and my_cash - 10 >= 0):
                            self.merc_east_count += 1
                        elif (next_merc_direction == "W" and my_cash - 10 >= 0):
                            self.merc_west_count += 1
                        return AIAction("build", crossbow_max[0], crossbow_max[1], "crossbow", merc_direction=next_merc_direction)
                elif minigun_max[2] >= crossbow_max[2] and minigun_max[2] >= cannon_max[2]:
                    if (my_cash - self.minigun_tuple[0]) >= 0:
                        self.num_miniguns += 1
                    if (prov_chance == 0):
                        if (next_merc_direction == "N" and my_cash - 10 >= 0):
                            self.merc_north_count += 1
                        elif (next_merc_direction == "S" and my_cash - 10 >= 0):
                            self.merc_south_count += 1
                        elif (next_merc_direction == "E" and my_cash - 10 >= 0):
                            self.merc_east_count += 1
                        elif (next_merc_direction == "W" and my_cash - 10 >= 0):
                            self.merc_west_count += 1
                        return AIAction("build", minigun_max[0], minigun_max[1], "minigun", merc_direction=next_merc_direction, provoke_demons=True)
                    else:
                        if (next_merc_direction == "N" and my_cash - 10 >= 0):
                            self.merc_north_count += 1
                        elif (next_merc_direction == "S" and my_cash - 10 >= 0):
                            self.merc_south_count += 1
                        elif (next_merc_direction == "E" and my_cash - 10 >= 0):
                            self.merc_east_count += 1
                        elif (next_merc_direction == "W" and my_cash - 10 >= 0):
                            self.merc_west_count += 1
                        return AIAction("build", minigun_max[0], minigun_max[1], "minigun", merc_direction=next_merc_direction)
                
            #elif (num_towers / self.num_houses) > 3/2 and num_towers >= 1:
            elif rand_num == 2:
                merc_directions = get_available_queue_directions(game_state, self.team_color)
                direction_counts = []
                for direction in merc_directions:
                    if direction == "N":
                        direction_counts.append(self.merc_north_count)
                    elif direction == "S":
                        direction_counts.append(self.merc_south_count)
                    elif direction == "E":
                        direction_counts.append(self.merc_east_count)
                    elif direction == "W":
                        direction_counts.append(self.merc_west_count)
                
                next_merc_direction = merc_directions[direction_counts.index(min(direction_counts))]

                if prov_chance == 0:
                    if (next_merc_direction == "N" and my_cash - 10 >= 0):
                        self.merc_north_count += 1
                    elif (next_merc_direction == "S" and my_cash - 10 >= 0):
                        self.merc_south_count += 1
                    elif (next_merc_direction == "E" and my_cash - 10 >= 0):
                        self.merc_east_count += 1
                    elif (next_merc_direction == "W" and my_cash - 10 >= 0):
                        self.merc_west_count += 1
                    return AIAction("nothing",0,0,merc_direction=next_merc_direction, provoke_demons=True)
                else:
                    if (next_merc_direction == "N" and my_cash - 10 >= 0):
                        self.merc_north_count += 1
                    elif (next_merc_direction == "S" and my_cash - 10 >= 0):
                        self.merc_south_count += 1
                    elif (next_merc_direction == "E" and my_cash - 10 >= 0):
                        self.merc_east_count += 1
                    elif (next_merc_direction == "W" and my_cash - 10 >= 0):
                        self.merc_west_count += 1
                    return AIAction("nothing",0,0,merc_direction=next_merc_direction)

        return AIAction("nothing",0,0)

        # -- YOUR CODE ENDS HERE --


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