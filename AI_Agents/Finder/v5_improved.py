import sys
import json
import random
from typing import List, Tuple, Dict

# --- AI ACTION CLASS ---
class AIAction:
    def __init__(
        self,
        action: str,
        x: int,
        y: int,
        tower_type: str = "",
        merc_direction: str = "",
        provoke_demons: bool = False
    ):
        self.action = action.lower().strip()
        self.x = x
        self.y = y
        self.tower_type = tower_type.strip()
        self.merc_direction = merc_direction.upper().strip()
        self.provoke_demons = provoke_demons
    
    def to_dict(self):
        return {
            'action': self.action,
            'x': self.x,
            'y': self.y,
            'tower_type': self.tower_type,
            'merc_direction': self.merc_direction,
            'provoke_demons': self.provoke_demons
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())

# --- HELPER FUNCTIONS ---
def is_out_of_bounds(game_state: dict, x: int, y: int) -> bool:
    return x < 0 or x >= len(game_state['FloorTiles'][0]) or y < 0 or y >= len(game_state['FloorTiles'])

def get_available_queue_directions(game_state: dict, team_color: str) -> List[str]:
    result = []
    offsets = {(0, -1): "N", (0, 1): "S", (1, 0): "E", (-1, 0): "W"}
    player = game_state['PlayerBaseR'] if team_color == 'r' else game_state['PlayerBaseB']
    for dx, dy in offsets.keys():
        x, y = player['x'] + dx, player['y'] + dy
        if not is_out_of_bounds(game_state, x, y) and game_state['FloorTiles'][y][x] == "O":
            result.append(offsets[(dx, dy)])
    return result

def get_available_build_spaces(game_state: dict, team_color: str) -> List[Tuple[int,int]]:
    result = []
    for y, row in enumerate(game_state['FloorTiles']):
        for x, c in enumerate(row):
            if c == team_color and game_state['EntityGrid'][y][x] == '':
                result.append((x, y))
    return result

def get_my_towers(game_state: dict, team_color: str) -> List[dict]:
    return [t for t in game_state['Towers'] if t["Team"] == team_color]

def get_my_money(game_state: dict, team_color: str) -> int:
    return game_state["RedTeamMoney"] if team_color == 'r' else game_state["BlueTeamMoney"]

def get_tower_prices(game_state: dict, team_color: str) -> Dict[str, int]:
    return game_state["TowerPricesR"] if team_color == 'r' else game_state["TowerPricesB"]

def count_houses(towers: List[dict]) -> int:
    return sum(1 for t in towers if t['Type'].lower() == 'house')

# --- ULTRA AGGRESSIVE SIMPLE AGENT ---
class UltraAggressiveAgent:
    def initialize_and_set_name(self, initial_game_state: dict, team_color: str) -> str:
        self.team_color = team_color
        return "UltraAggressive_v9"

    def do_turn(self, game_state: dict) -> AIAction:
        turn = game_state["CurrentTurn"]
        my_money = get_my_money(game_state, self.team_color)
        build_spaces = get_available_build_spaces(game_state, self.team_color)
        q_dirs = get_available_queue_directions(game_state, self.team_color)
        my_towers = get_my_towers(game_state, self.team_color)
        prices = get_tower_prices(game_state, self.team_color)
        house_count = count_houses(my_towers)
        
        provoke = False
        
        # Turn 0: Build house
        if turn == 0:
            if build_spaces:
                pos = random.choice(build_spaces)
                return AIAction("build", pos[0], pos[1], 'house', provoke_demons=provoke)
        
        # Turns 1-30: HOUSE SPAM + MERC SPAM
        if turn < 27:
            # Merc probability increases from 50% to 80% over turns 1-29
            merc_probability = 0.5 + (turn / 60.0)
            
            # Try to send merc based on probability
            if my_money >= 10 and q_dirs and random.random() < merc_probability:
                return AIAction("nothing", 0, 0, merc_direction=random.choice(q_dirs), provoke_demons=provoke)
            
            # Build house if we can
            if build_spaces and my_money >= prices['House']:
                pos = random.choice(build_spaces)
                # Try to also send merc
                merc_dir = random.choice(q_dirs) if q_dirs and my_money - prices['House'] >= 10 else ''
                return AIAction("build", pos[0], pos[1], 'house', merc_direction=merc_dir, provoke_demons=provoke)
            
            # Can't build, just send merc
            if q_dirs and my_money >= 10:
                return AIAction("nothing", 0, 0, merc_direction=random.choice(q_dirs), provoke_demons=provoke)
        
        # Turn 30+: TOWER SPAM + MERC SPAM
        else:
            if build_spaces:
                # Simple tower selection
                tower_type = random.choice(['cannon', 'crossbow', 'cannon', 'crossbow', 'minigun', 'church'])
                
                if my_money >= prices[tower_type.capitalize()]:
                    pos = random.choice(build_spaces)
                    merc_dir = random.choice(q_dirs) if q_dirs and my_money - prices[tower_type.capitalize()] >= 10 else ''
                    return AIAction("build", pos[0], pos[1], tower_type, 
                                  merc_direction=merc_dir, provoke_demons=provoke)
            
            # No space - destroy tower if late
            if not build_spaces and len(my_towers) > 0 and turn >= 50:
                for tower in my_towers:
                    if tower['Type'].lower() != 'house':
                        return AIAction("destroy", tower['x'], tower['y'], provoke_demons=provoke)
            
            # Just spam mercs
            if q_dirs and my_money >= 10:
                return AIAction("nothing", 0, 0, merc_direction=random.choice(q_dirs), provoke_demons=provoke)
        
        return AIAction("nothing", 0, 0, provoke_demons=provoke)

# --- DRIVER CODE ---
if __name__ == '__main__':
    team_color = 'r' if input() == "--YOU ARE RED--" else 'b'

    input_buffer = [input()]
    while input_buffer[-1] != "--END INITIAL GAME STATE--":
        input_buffer.append(input())
    game_state_init = json.loads(''.join(input_buffer[:-1]))

    agent = UltraAggressiveAgent()
    print(agent.initialize_and_set_name(game_state_init, team_color))
    print(agent.do_turn(game_state_init).to_json())

    while True:
        input_buffer = [input()]
        while input_buffer[-1] != "--END OF TURN--":
            input_buffer.append(input())
        game_state_this_turn = json.loads(''.join(input_buffer[:-1]))
        print(agent.do_turn(game_state_this_turn).to_json())