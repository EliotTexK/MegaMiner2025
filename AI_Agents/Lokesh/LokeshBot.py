import sys
import json
import string
import json

# Any imports from the standard library are allowed
import random
import math

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

#my helper function
def get_good_position_4house(opponentBase_x: int, opponentBase_y: int, build_space: list, demon_spawners: list, game_state: dict, team_color: str):
    
    if not build_space:
        return None, None
    
    best_position = None
    best_score = -999
    map_width = len(game_state["FloorTiles"][0])

    for (x,y) in build_space:
        score = 0
        score += math.pow((x - opponentBase_x), 2) + math.pow((y - opponentBase_y), 2)

        if team_color == 'r':
            score += x * 20
        else:
            score += (map_width - x) * 20

        for spawner in demon_spawners:
            spawner_x = spawner["x"]
            spawner_y = spawner["y"]

            dist = abs(x - spawner_x) + abs(y - spawner_y)

            score += dist * 20

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                neighbor_x, neighbor_y = x+dx, y+dy
                if not is_out_of_bounds(game_state, neighbor_x, neighbor_y):
                    if game_state["FloorTiles"][neighbor_y][neighbor_x] == "O":
                        score -= 30
        
        for t in game_state["Towers"]:
            if t["Team"] == team_color and t["Type"] == "House":
                d = abs(x-t["x"]) + abs(y - t["y"])
                if d < 3:
                    score -= 50

        if score > best_score:
            best_score = score
            best_position = (x,y)
    
    return best_position

def get_good_position_4defense(build_spaces: list, game_state: dict, myBase_x: int, myBase_y: int, team_color):
    # define the direction

    if not build_spaces:
        return None, None
    
    best_position = build_spaces[0]
    best_score = -9999

    max_range = 3

    for (x, y) in build_spaces:
        path_hits = 0
        # Check all 4 neighbors
        for dy in range(-max_range, max_range +1):
            for dx in range(-max_range, max_range +1):
                if abs(dx) + abs(dy) <= max_range:
                    neighbor_x = x + dx
                    neighbor_y = y + dy
            

                    # validate the neighbors
                    if not is_out_of_bounds(game_state, neighbor_x, neighbor_y):
                        if game_state["FloorTiles"][neighbor_y][neighbor_x] == 'O':
                            path_hits += 1

        if team_color == 'b':
            path_score = -x
        else:
            path_score = x
        
        dist_base = abs(x - myBase_x) + abs(y - myBase_y)

        score = path_hits * 10 + path_score - dist_base

        if score > best_score:
            best_score = score
            best_position = (x, y)
    
    return best_position

# -- AGENT CLASS (COMPETITORS WILL IMPLEMENT THIS) --
class Agent:
    def initialize_and_set_name(self, initial_game_state: dict, team_color: str) -> str:
    
        # Competitors: Do any initialization here
        self.initial_game_state = initial_game_state

        # It's essential that you keep track of which team you're on
        self.team_color = team_color

        # Return a string representing your team's name
        return "Yalamber"
    
    # Take in a dictionary representing the game state, then output an AI Action
    def do_turn(self, game_state: dict) -> AIAction:

        # Get the following data using helper function
        queue_direction = get_available_queue_directions(game_state, self.team_color)
        build_spaces = get_available_build_spaces(game_state, self.team_color)
        my_money = get_my_money_amount(game_state, self.team_color)
        my_towers = get_my_towers(game_state, self.team_color)

        turn = game_state["CurrentTurn"]
        
        # Store the previous turn to take strategic action action against enemy
        prev_turn = turn - 1 if turn != 1 else 0

        # Find out the oponent team Color and opponent's geography
        opponent_color = 'r' if self.team_color == 'b' else 'b'

        opponentBase_x, opponentBase_y = 0, 0
        myBase_x, myBase_y = 0, 0

        if opponent_color == 'r':
            opponentBase_x = game_state["PlayerBaseR"]["x"]
            opponentBase_y = game_state["PlayerBaseR"]["y"]
        else:
            opponentBase_x = game_state["PlayerBaseB"]["x"]
            opponentBase_y = game_state["PlayerBaseB"]["y"]
        
        if self.team_color == 'r':
            myBase_x = game_state["PlayerBaseR"]["x"]
            myBase_y = game_state["PlayerBaseR"]["y"]
        else:
            myBase_x = game_state["PlayerBaseB"]["x"]
            myBase_y = game_state["PlayerBaseB"]["y"]

        # find out the location of demon spawners:
        demon_spawners = game_state["DemonSpawners"]

        #check the demon threat near me
        min_demon_dist = 1000 # placeholder
        for demon in game_state["Demons"]:
            dx = demon["x"] - myBase_x
            dy = demon["y"] - myBase_y
            dist = abs(dx) + abs(dy)
            if dist< min_demon_dist:
                min_demon_dist = dist

        # check enemy mercenary threat near my base
        min_merc_dist = 1000
        for merc in game_state["Mercenaries"]:
            if merc["Team"] != self.team_color:
                dx = merc["x"] - myBase_x
                dy = merc["y"] - myBase_y
                dist = abs(dx) + abs(dy)
                if dist < min_merc_dist:
                    min_merc_dist = dist

        close_threat_dist = min(min_demon_dist, min_merc_dist)
        under_demon_threat = (close_threat_dist <= 3)


        # add more safety rule
        defense_build_spaces = []
        
        for (i , j) in build_spaces:
            if j >= myBase_y:
                defense_build_spaces.append((i,j))

        if len(defense_build_spaces) == 0:
            defense_build_spaces = build_spaces

        #Get the prices of all the things
        prices = game_state["TowerPricesR"] if self.team_color == 'r' else game_state["TowerPricesB"]
        
        #set the counter to 0 in each turn
        num_houses = 0
        num_cannon = 0
        num_crossbows = 0
        num_miniguns = 0
        num_church = 0

        # also count the opponent houses
        opponent_houses = 0
        opponent_defenses = 0

        #get the number of house
        for tower in game_state["Towers"]:
            if tower["Team"] == self.team_color:
                if tower["Type"] == "House":
                    num_houses += 1
                elif tower["Type"] == "Crossbow":
                    num_crossbows += 1
                elif tower["Type"] == "Cannon":
                    num_cannon += 1
                elif tower["Type"] == "Minigun":
                    num_miniguns += 1
                elif tower["Type"] == "Church":
                    num_church += 1
            else:
                if tower["Type"] == "House":
                    opponent_houses += 1
                elif tower["Type"] in ["Crossbow", "Cannon", "Minigun", "Church"]:
                    opponent_defenses += 1

        # get the price of a house:
        housePrice = prices["House"]

        #get the price of a crossbow:
        crossbowPrice = prices["Crossbow"]

        #get the price of a cannons:
        cannonsPrice = prices["Cannon"]

        #get the price of a miniGun:
        minigunPrice = prices["Minigun"]

        #get the price of a church:
        churchPrice = prices["Church"]

        mercDir = ""
        provoke = False

        total_defense = num_cannon + num_crossbows + num_miniguns

        # My policy - offensive is the best defensive
        if len(queue_direction) > 0 and my_money >= 10:
            safe_to_attack = (not under_demon_threat) or (total_defense >= 2)

            if safe_to_attack:
                if turn > 15 and total_defense >= 2:
                    mercDir = queue_direction[0]
                #attack if no defenses with enemy
                elif opponent_defenses == 0 and turn > 10:
                    mercDir = queue_direction[0]

        if (not under_demon_threat) and turn > 60 and num_cannon >= 2 and num_miniguns >= 1 and my_money >= 10:
            provoke = True
        
        # no provoke and mer_dir in panic situation
        # handle the panic situation:
        if under_demon_threat and len(defense_build_spaces) > 0:
            if cannonsPrice <= my_money:

                panic_x, panic_y = get_good_position_4defense(
                    defense_build_spaces,
                    game_state,
                    myBase_x,
                    myBase_y,
                    self.team_color
                )

                if panic_x is not None:
                    return AIAction("build", panic_x, panic_y, "cannon", merc_direction="", provoke_demons=False)
            
            if minigunPrice <= my_money:

                panic_x, panic_y = get_good_position_4defense(
                    defense_build_spaces,
                    game_state,
                    myBase_x,
                    myBase_y,
                    self.team_color
                )

                if panic_x is not None:
                    return AIAction("build", panic_x, panic_y, "minigun", merc_direction="", provoke_demons=False)
                
            if crossbowPrice <= my_money:
                panic_x, panic_y = get_good_position_4defense(
                    defense_build_spaces,
                    game_state,
                    myBase_x,
                    myBase_y,
                    self.team_color
                )
                if panic_x is not None:
                    return AIAction("build", panic_x, panic_y, "crossbow", merc_direction="", provoke_demons=False)
                
        # get houses first
        if (not under_demon_threat) and num_houses < 1 and turn < 100:
            if len(build_spaces) > 0 and housePrice <= my_money:

                house_x, house_y = get_good_position_4house(
                    opponentBase_x,
                    opponentBase_y,
                    build_spaces,
                    demon_spawners,
                    game_state,
                    self.team_color
                )

                if house_x is not None and house_y is not None:
                    return AIAction("build", house_x, house_y, 'house', merc_direction=random.choice(queue_direction), provoke_demons=provoke)


        # get the cheapest canon first as entry level protection
        if num_cannon < 1:
            if len(defense_build_spaces) > 0 and cannonsPrice <= my_money:
                cannon_x, cannon_y = get_good_position_4defense(
                    defense_build_spaces,
                    game_state,
                    myBase_x,
                    myBase_y,
                    self.team_color
                )
                if cannon_x is not None:

                    return AIAction("build",
                        cannon_x,
                        cannon_y,
                        "cannon",
                        merc_direction=mercDir, provoke_demons=provoke
                    )

        # PRIORITY 3: Get first Crossbow (for single targets)
        if num_crossbows < 1:
            if len(defense_build_spaces) > 0 and crossbowPrice <= my_money:
                crossBow_x, crossBow_y = get_good_position_4defense(
                    defense_build_spaces,
                    game_state,
                    myBase_x,
                    myBase_y,
                    self.team_color
                )

                if crossBow_x is not None:
                    return AIAction("build", crossBow_x, crossBow_y, 'crossbow',
                        merc_direction=mercDir, provoke_demons=provoke
                    )

        # build economy if alive
        if num_houses < 4 and turn < 160:
            if (not under_demon_threat) or (total_defense >= 2):
                if len(build_spaces) > 0 and housePrice <= my_money:
                    house_x, house_y = get_good_position_4house(
                        opponentBase_x,
                        opponentBase_y,
                        build_spaces,
                        demon_spawners,
                        game_state,
                        self.team_color
                    )
                    if house_x is not None:
                        return AIAction("build",
                            house_x,
                            house_y,
                            'house',
                            merc_direction=mercDir,
                            provoke_demons=provoke
                        )

        # cannon ratio
        if (num_crossbows >= num_cannon * 2):
            if cannonsPrice <= my_money and len(defense_build_spaces) > 0:
                cannon_x, cannon_y = get_good_position_4defense(
                    defense_build_spaces,
                    game_state,
                    myBase_x,
                    myBase_y,
                    self.team_color
                )
                if cannon_x is not None:
                    return AIAction("build", cannon_x, cannon_y, "cannon", merc_direction=random.choice(queue_direction), provoke_demons=provoke)

        # Minigun : add more power to arsenal
        if (num_crossbows >= num_miniguns * 4):
            if minigunPrice <= my_money and len(defense_build_spaces) > 0:
                minigun_x, minigun_y = get_good_position_4defense(
                    defense_build_spaces,
                    game_state,
                    myBase_x,
                    myBase_y,
                    self.team_color
                )
                if minigun_x is not None:
                    return AIAction("build", minigun_x, minigun_y, "minigun", merc_direction=mercDir, provoke_demons=provoke)

        # build church in good condition
        if (not under_demon_threat) and num_church < 1 and num_houses >= 2 and total_defense >= 2:
            if churchPrice <= my_money and len(defense_build_spaces) > 0:
                church_x, church_y = get_good_position_4defense(
                        defense_build_spaces,
                        game_state,
                        myBase_x,
                        myBase_y,
                        self.team_color
                    )

                if church_x is not None:
                    return AIAction("build", church_x, church_y, 'church', merc_direction=mercDir, provoke_demons=provoke)

        # default good tower
        if len(defense_build_spaces) > 0 and crossbowPrice <= my_money:
            crossBow_x, crossBow_y = get_good_position_4defense(
                defense_build_spaces,
                game_state,
                myBase_x,
                myBase_y,
                self.team_color
            )
            if crossBow_x is not None:
                return AIAction("build", crossBow_x, crossBow_y, 'crossbow', merc_direction=mercDir, provoke_demons=provoke)
        
        # FALLBACK
        else:
            return AIAction("nothing", 0, 0, merc_direction=mercDir, provoke_demons=provoke)


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