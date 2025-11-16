#Programmer: Alexander Willimas
#Extremely messy and all over the place, however its Python so I don't care, basically I just wrote a new function whenever I needed something rather than checking if any of my other functions could be adapted instead

import sys
import json
import string
import json

# Any imports from the standard library are allowed
import random

from typing import Optional
import json

IS_EARLY_GAME = False
IS_MID_GAME = False
IS_LATE_GAME = False

TOWER_RANGES = {
    "Crossbow": 5,
    "Cannon": 3,
    "Minigun": 3,
    "Church": 3,
    "House": 0
}

DEMON_STATS = {
    "LEVEL": 1,
    "HEALTH": 15,
    "DAMAGE": 10
}

DEMON_SIGHTINGS = 0

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

#AI FUNCTIONS I WROTE

#Builds array for tiles
def get_path_tiles(game_state):
    result = []
    for y, row in enumerate(game_state["FloorTiles"]):
        for x, c in enumerate(row):
            if c== "O":
                result.append((x, y))

    return result

#Self explanitory, for calculating enemy threat level and optimal housing placements
def get_base_distances(game_state, team, x, y):
    my_base = game_state["PlayerBaseR"] if team == "r" else game_state["PlayerBaseB"]
    enemy_base = game_state["PlayerBaseB"] if team == "r" else game_state["PlayerBaseR"]

    d_my = abs(x - my_base["x"]) + abs(y - my_base["y"])
    d_enemy = abs(x - enemy_base["x"]) + abs(y - enemy_base["y"])
    return d_my, d_enemy

#For calculating demon threat level
def update_demons(game_state):
    global DEMON_SIGHTINGS, DEMON_STATS

    total_now = 0

    total_now = len(game_state["Demons"])

    if total_now > DEMON_SIGHTINGS:
        DEMON_STATS["DAMAGE"] += 3
        DEMON_STATS["HEALTH"] += 5
        DEMON_STATS["LEVEL"] += 1

    DEMON_SIGHTINGS = total_now

#Lane Class and Helpers
#THIS IS THE MAIN STAPLE OF THIS AI. I actually seperate the tiles into a list of this lane object, then attach a bunch of attributes related to the lane so the ai know what it should be defending/offending

class Lane:
    def __init__(self, tiles, spawn_direction=""):
        self.tiles = tiles
        self.length = len(tiles)

        self.spawn_direction = spawn_direction

        self.spawner_count = 0

        self.ally_mercs = []
        self.enemy_mercs = []
        self.demons = []

        self.ally_towers = []
        self.enemy_towers = []

        self.in_range_turrets = 0
        self.in_range_enemy_turrets = 0

        self.threat_score = 0 #If laned need defending
        self.pressure_score = 0 #Focus offence on the same lane if the opportunity presents itself

        self.being_attacked = False #Need to defend this lane right now
        self.attacking = False #Fighting the enemy base

    def __repr__(self):
        return f"<Lane dir={self.spawn_direction} len={self.length} spawns={self.spawner_count}>"
    
    def compute_tower_coverage(self, game_state, team):
        self.ally_towers = []
        self.enemy_towers = []

        self.in_range_enemy_turrets = 0
        self.in_range_turrets = 0

        towers = game_state["Towers"]

        for t in towers:
            t_type = t["Type"]
            tx, ty = t["x"], t["y"]
            tr = TOWER_RANGES[t_type]

            if tr == 0:
                continue

            covered_tiles = 0
            for (px, py) in self.tiles:
                if abs(px - tx) + abs(py - ty) <= tr:
                    covered_tiles += 1

            if covered_tiles > 0:
                if t["Team"] == team:
                    self.ally_towers.append((t, covered_tiles))
                    self.in_range_turrets += covered_tiles
                else:
                    self.enemy_towers.append((t, covered_tiles))
                    self.in_range_enemy_turrets += covered_tiles

    def compute_pressure_score(self, game_state, team):
        global DEMON_STATS
        
        merc_score = 0

        demon_score = 0

        enemy_block = len(self.enemy_mercs) * 25

        enemy_tower_pressure = self.in_range_enemy_turrets * 2

        for m in self.ally_mercs:
            d_my, d_enemy = get_base_distances(game_state, team, m["x"], m["y"])
            if d_enemy <= 3:
                self.attacking = True
            if d_enemy < 10:
                merc_score += (10 - d_enemy) * 5
            merc_score += 10

        for d in self.demons:
            d_my, d_enemy = get_base_distances(game_state, team, d["x"], d["y"])

            level = DEMON_STATS["LEVEL"]

            if d_enemy <= 3:
                self.attacking = True
            if d_enemy < 10:
                demon_score += (10 - d_my) * (level * 6) * (-1)
            demon_score += level * 5


        for tower, coverage in self.enemy_towers:
            t_type = tower["Type"]
            if t_type == "Cannon":
                enemy_tower_pressure += coverage * 10
            elif t_type == "Minigun":
                enemy_tower_pressure += coverage * 25
            elif t_type == "Church":
                enemy_block *= 1.1 * coverage

        ally_support = self.in_range_turrets * 2

        length_bonus = self.length * 0.5

        self.pressure_score = (
            merc_score + ally_support - length_bonus - enemy_block - demon_score - enemy_tower_pressure
        )

    def compute_threat_score(self, game_state, team):
        global DEMON_STATS

        merc_score = 0

        allied_merc_score = 0

        demon_score = 0
        
        spawner_score = 0
        
        tower_score = 0

        self.being_attacked = False

        spawn_blocked_penaly = 0

        if not can_spawn_merc_in_lane(game_state, team, self):
            spawn_blocked_penaly = -50

        for m in self.ally_mercs:
            d_my, d_enemy = get_base_distances(game_state, team, m["x"], m["y"])
            if d_my < 3:
                allied_merc_score += 50
            allied_merc_score += 10


        for m in self.enemy_mercs:
            d_my, d_enemy = get_base_distances(game_state, team, m["x"], m["y"])
            if d_my <= 4:
                self.being_attacked = True
            if d_my < 10:
                merc_score += (10 - d_my) * 10
            merc_score += 10

        for d in self.demons:
            d_my, d_enemy = get_base_distances(game_state, team, d["x"], d["y"])

            level = DEMON_STATS["LEVEL"]

            if d_my <= 4:
                self.being_attacked = True

            if d_my < 10:
                demon_score += (10 - d_my) * (level * 10)

            demon_score += level * 5

        spawner_score = self.spawner_count * (DEMON_STATS["LEVEL"] * 3)

        for tower, cov in self.enemy_towers:
            ttype = tower["Type"]
            if ttype == "Minigun":
                tower_score += cov * 3
            elif ttype == "Cannon":
                tower_score += cov * 2
            elif ttype == "Crossbow":
                tower_score += cov * 1

        self.threat_score = (
            merc_score +
            demon_score +
            spawner_score +
            tower_score + spawn_blocked_penaly - allied_merc_score
        )

#For adding the moving units to each lane
def get_closest_lane(lanes, x, y):
    best_lane = None
    best_dist = 999999

    for lane in lanes:
        for (px, py) in lane.tiles:
            dist = abs(x - px) + abs(y - py)
            if dist < best_dist:
                best_dist = dist
                best_lane = lane

    return best_lane

def assign_units_to_lanes(game_state, team, lanes):

    for lane in lanes:
        lane.being_attacked = False
        lane.ally_mercs = []
        lane.enemy_mercs = []
        lane.demons = []
        lane.spawner_count = 0

    for m in game_state["Mercenaries"]:
        lane = get_closest_lane(lanes, m["x"], m["y"])
        if lane is None:
            continue

        if m["Team"] == team:
            lane.ally_mercs.append(m)
        else:
            lane.enemy_mercs.append(m)

    for d in game_state["Demons"]:
        lane = get_closest_lane(lanes, d["x"], d["y"])
        if lane is None:
            continue

        lane.demons.append(d)

    for sp in game_state["DemonSpawners"]:
        lane = get_closest_lane(lanes, sp["x"], sp["y"])
        if lane:
            lane.spawner_count += 1

#Depth-First Search for lanemaking purposes, I guess I didn't need team in the parameters but oh well
def create_lanes(game_state, team):
    path_tiles = set(get_path_tiles(game_state))

    b_base = game_state["PlayerBaseB"]

    r_base = game_state["PlayerBaseR"]

    if team == "r":
        bx, by = r_base["x"], r_base["y"]
        rx, ry = b_base["x"], b_base["y"]
    else:
        rx, ry = r_base["x"], r_base["y"]
        bx, by = b_base["x"], b_base["y"]

        


    spawn_offsets = {
        "N": (0, -1),
        "S": (0,  1),
        "W": (-1, 0),
        "E": (1,  0)
    }

    lanes = []

    def trace_lane(start_x, start_y):
        visited = set()
        visited.add((bx, by))
        visited.add((rx, ry))
        tiles = []

        def dfs(x, y):
            if (x, y) in visited:
                return
            if (x, y) not in path_tiles:
                return

            visited.add((x, y))
            tiles.append((x, y))

            dfs(x+1, y)
            dfs(x-1, y)
            dfs(x, y+1)
            dfs(x, y-1)

        dfs(start_x, start_y)
        return tiles

    for dir_label, (ox, oy) in spawn_offsets.items():
        sx, sy = bx + ox, by + oy

        if (sx, sy) in path_tiles:
            lane_tiles = trace_lane(sx, sy)
            if lane_tiles:
                lanes.append(Lane(lane_tiles, spawn_direction=dir_label))

    return lanes


def can_spawn_merc_in_lane(game_state, team, lane):
    direction = lane.spawn_direction
    base = game_state["PlayerBaseR"] if team == "r" else game_state["PlayerBaseB"]
    bx, by = base["x"], base["y"]

    if direction == "N":
        tx, ty = bx, by - 1
    elif direction == "S":
        tx, ty = bx, by + 1
    elif direction == "E":
        tx, ty = bx + 1, by
    elif direction == "W":
        tx, ty = bx - 1, by
    else:
        return False

    grid = game_state["EntityGrid"]
    return (grid[ty][tx] is None) or (grid[ty][tx] == "")


#For threat calculation and housing placements
def get_demon_spawners(game_state):
    return [(d["x"], d["y"]) for d in game_state["DemonSpawners"]]



#Get Important Defensive Locations, these kind of do the same thing but oh well
def near_path(tile, path_tiles, dis):
    x, y = tile
    for (px, py) in path_tiles:
        if abs(x - px) + abs(y - py) <= dis:
            return True
    return False

def path_range_score(x, y, path_tiles, tower_range):
    score = 0
    for (px, py) in path_tiles:
        dist = abs(x - px) + abs(y - py)
        if abs(x - px) + abs(y - py) <= tower_range:
            score += (tower_range - dist + 1)
    return score


#Tower PLace Functions

def choose_house_spot(game_state, team):
    build_spaces = get_available_build_spaces(game_state, team)
    if not build_spaces:
        return None

    path_tiles = get_path_tiles(game_state)
    demon_spawns = get_demon_spawners(game_state)

    best_score = -999999
    best_tile = None

    for (x, y) in build_spaces:

        # distance to nearest path
        d_path = d_path = min((x - px)**2 + (y - py)**2 for (px, py) in path_tiles)

        # distance to nearest spawner
        d_spawn = min(abs(x - sx) + abs(y - sy) for (sx, sy) in demon_spawns)

        # distance from bases
        d_my, d_enemy = get_base_distances(game_state, team, x, y)


        # near path penalty
        near_path_penalty = 300 if near_path((x, y), path_tiles, 1) else 30 if near_path((x, y), path_tiles, 2) else 0

        score = (
            d_path * 10 +
            d_spawn  +
            d_enemy * 2 + d_my -
            near_path_penalty
        )

        if score > best_score:
            best_score = score
            best_tile = (x, y)

    if not path_tiles or not best_tile:
        return random.choice(build_spaces)

    return best_tile

def get_house_location(game_state, team):
    houses = []

    for tower in game_state["Towers"]:
        if tower["Team"] == team and tower["Type"] == "House":
            houses.append((tower["x"], tower["y"]))
    return houses

def get_bad_house(game_state, team):
    house_locations = get_house_location(game_state, team)

    path_tiles = get_path_tiles(game_state)
    demon_spawns = get_demon_spawners(game_state)

    best_score = -999999
    best_tile = None

    for (x, y) in house_locations:

        # distance to nearest path
        d_path = d_path = min((x - px)**2 + (y - py)**2 for (px, py) in path_tiles)

        # distance to nearest spawner
        d_spawn = min(abs(x - sx) + abs(y - sy) for (sx, sy) in demon_spawns)

        # distance from enemy base
        d_my, d_enemy = get_base_distances(game_state, team, x, y)


        # backline preference
        back_score = d_enemy

        # near path penalty
        near_path_penalty = 300 if near_path((x, y), path_tiles, 1) else 30 if near_path((x, y), path_tiles, 2) else 0

        score = (
            near_path_penalty -
            d_path * 10 -
            d_spawn * 2 -
            d_enemy * 1 -
            back_score * 1
        )

        if score > best_score:
            best_score = score
            best_tile = (x, y)

    if not path_tiles or not best_tile:
        return random.choice(house_locations)

    return best_tile


def choose_defense_spot(game_state , team, tower_range):
    build_spaces = get_available_build_spaces(game_state, team)
    if not build_spaces:
        return None
    
    path_tiles = get_path_tiles(game_state)

    best_score = -999999
    best_tile = None

    for (x, y) in build_spaces:

        path_score = path_range_score(x, y, path_tiles, tower_range)
        d_my, d_enemy = get_base_distances(game_state, team, x, y)

        proximity_path_bonus = 1 if near_path((x, y), path_tiles, 1) else 0
        my_proximity_penalty = -3 if d_my <= 2 else 2 if 2 < d_my <= tower_range else 0
        enemy_proximity_penalty = -3 if d_my <= 2 else 1 if 2 < d_enemy <= tower_range else 0
        

        score = path_score * 20 + proximity_path_bonus * 20 + my_proximity_penalty * 2 + enemy_proximity_penalty * 2

        if path_score == 0:
            score = 0

        if score > best_score:
            best_score = score
            best_tile = (x, y)

    return best_tile


def build_house(game_state, team):
    spot = choose_house_spot(game_state, team)
    if spot is not None:
        x, y = spot
        return AIAction("build", x, y, "house")
#completely unsused lol
def compute_future_money(game_state, team_color, turns=2):
    money = get_my_money_amount(game_state, team_color)
    towers = get_my_towers(game_state, team_color)

    income = 0
    for t in towers:
        if t["Type"] == "House":
            income += 12 / 5 * turns
    return money + income

def get_house_count(game_state, team):
    return sum(1 for t in game_state["Towers"]
               if t["Team"] == team and t["Type"] == "House")


#Main decision making logic

def analyze_lanes(game_state, lanes, team):

    emergency_lane = None
    best_defense_lane = None
    best_attack_lane = None

    if lanes:
        best_defense_lane = max(lanes, key=lambda ln: ln.threat_score)
        best_attack_lane = max(lanes, key=lambda ln: ln.pressure_score)

    for lane in lanes:
        if getattr(lane, "being_attacked", False) or lane.threat_score >= 200:
            if emergency_lane is None or lane.threat_score > emergency_lane.threat_score:
                emergency_lane = lane

    return {
        "emergency_lane": emergency_lane,
        "best_defense_lane": best_defense_lane,
        "best_attack_lane": best_attack_lane,
    }

def get_tower_price(game_state, team, tower):
    price = game_state[f"TowerPrices{team.upper()}"][tower.capitalize()]
    return price

def afford_merc_and_tower(game_state, team, tower, money):
    if money >= get_tower_price(game_state, team, tower) + 10:
        return True
    else:
        return False

def evaluate_tower_value(game_state, team, lanes, tower_type):

    church_weight = 1

    if IS_LATE_GAME:
        church_weight = 3

    # Role weights
    ROLE_WEIGHT = {
        "crossbow": 0.8,
        "cannon": 1.2,
        "minigun": 2.0,
        "church": 0.7 * church_weight
    }

    tower_range = TOWER_RANGES[tower_type.capitalize()]

    total_coverage_score = 0
    total_lane_threat   = 0
    total_lane_pressure = 0

    for lane in lanes:
        lane_threat = lane.threat_score
        lane_pressure = lane.pressure_score

        max_cov = 0
        for (x, y) in lane.tiles:
            cov = sum(
                1 for (px, py) in lane.tiles
                if abs(px - x) + abs(py - y) <= tower_range
            )
            max_cov = max(max_cov, cov)

        total_coverage_score += max_cov
        total_lane_threat   += lane_threat
        total_lane_pressure += lane_pressure

    raw_value = (
        total_coverage_score * 1.0 +
        total_lane_threat   * 0.3 +
        total_lane_pressure * 0.2
    )

    return raw_value * ROLE_WEIGHT[tower_type.lower()]


def score_tower_placement(x, y, game_state, team, tower_type, lanes):
    path_tiles = get_path_tiles(game_state)
    tower_range = TOWER_RANGES[tower_type.capitalize()]
    if tower_range == 0:
        return -999  # Houses handled separately
    
    ROLE_WEIGHT = {
        "crossbow": 0.8,
        "cannon": 1.0,
        "minigun": 2.0,
        "church": 1.5
    }


    # Coverage = how many path tiles this specific tile reaches
    cov = path_range_score(x, y, path_tiles, tower_range)

    if cov == 0:
        return -999  # Never build where no path is reached

    # Distance from base (avoid crowding base early)
    d_my, d_enemy = get_base_distances(game_state, team, x, y)
    base_safety = 1 if d_my > 2 else -5

    # Lane-based threats
    lane_boost = 0
    for lane in lanes:
        if any(abs(x-px)+abs(y-py) <= tower_range for (px,py) in lane.tiles):
            lane_boost += lane.threat_score * 0.3
            lane_boost += lane.pressure_score * 0.15

    score = (
        cov * ROLE_WEIGHT[tower_type.lower()] +
        lane_boost +
        base_safety
    )

    return score

def choose_best_tower_and_location(game_state, team, lanes):
    money = get_my_money_amount(game_state, team)
    prices = game_state[f"TowerPrices{team.upper()}"]
    build_spaces = get_available_build_spaces(game_state, team)

    tower_types = ["crossbow", "cannon", "minigun", "church"]

    best_total_score = -999999
    best_choice = None

    for tower in tower_types:
        cost = prices[tower.capitalize()]

        if money < cost:
            continue
        

        global_value = evaluate_tower_value(game_state, team, lanes, tower)

        if money - cost < 10:
            global_value *= 0.3

        for (x, y) in build_spaces:
            loc_score = score_tower_placement(x, y, game_state, team, tower, lanes)
            if loc_score < 0:
                continue

            total = global_value + loc_score

            if total > best_total_score:
                best_total_score = total
                best_choice = (tower.lower(), x, y)

    return best_choice


# -- AGENT CLASS (COMPETITORS WILL IMPLEMENT THIS) --
class Agent:
    def initialize_and_set_name(self, initial_game_state: dict, team_color: str) -> str:
        # -- YOUR CODE BEGINS HERE --
        # Competitors: Do any initialization here        

        # It's essential that you keep track of which team you're on
        self.team_color = team_color

        self.turn = 0

        self.count = {
            "house": 0,
            "crossbow": 0,
            "cannon": 0,
            "minigun": 0,
            "church": 0
        }

        IS_EARLY_GAME = True

        self.lane_memory = {
            "N": { "early_merc_sent": False },
            "S": { "early_merc_sent": False },
            "E": { "early_merc_sent": False },
            "W": { "early_merc_sent": False },
        }


        # Return a string representing your team's name
        return "Alpha"
        # -- YOUR CODE ENDS HERE --
    
    # Take in a dictionary representing the game state, then output an AI Action
    def do_turn(self, game_state: dict) -> AIAction:
        # -- YOUR CODE BEGINS HERE --
        global IS_EARLY_GAME, IS_MID_GAME, IS_LATE_GAME

        self.turn = game_state["CurrentTurn"]

        if self.turn > 50:
            IS_EARLY_GAME = False
            IS_MID_GAME = False
            IS_LATE_GAME = True
        elif self.turn > 20:
            IS_EARLY_GAME = False
            IS_MID_GAME = True
            IS_LATE_GAME = False
        else:
            IS_EARLY_GAME = True
            IS_MID_GAME = False
            IS_LATE_GAME = False

        team = self.team_color
        money = get_my_money_amount(game_state, team)
        house_price = game_state[f"TowerPrices{team.upper()}"]["House"]

        demon_spam = money > 400 and random.choice([True, False])

        lanes = create_lanes(game_state, team)

        if not lanes:
            return AIAction("nothing", 0, 0, provoke_demons=demon_spam)

        assign_units_to_lanes(game_state, team, lanes)

        for lane in lanes:
            lane.compute_tower_coverage(game_state, team)
            lane.compute_pressure_score(game_state, team)
            lane.compute_threat_score(game_state, team)
            if len(lane.enemy_mercs) == 0 and len(lane.demons) == 0 and not lane.being_attacked:
                if lane.spawn_direction in self.lane_memory:
                    self.lane_memory[lane.spawn_direction]["early_merc_sent"] = False

        lane_info = analyze_lanes(game_state, lanes, team)
        emergency_lane = lane_info["emergency_lane"]
        best_defense_lane = lane_info["best_defense_lane"]
        best_attack_lane = lane_info["best_attack_lane"]

        build_spaces = get_available_build_spaces(game_state, team)
        merc_dirs = get_available_queue_directions(game_state, team)
        my_towers = get_my_towers(game_state, team)

        must_spawn_defensive_merc = False
        spawn_lane = None

        tower_choice = choose_best_tower_and_location(game_state, team, lanes)

#RED ALERT, WE GOT DUDES AT THE BASE
        if emergency_lane is not None:
            direction = emergency_lane.spawn_direction

            if not build_spaces and get_house_count(game_state, team) > 5:
                spot = get_bad_house(game_state, team)
                if spot is not None:
                    x, y = spot
                    return AIAction(
                        "destroy", x, y,
                        merc_direction=direction,
                        provoke_demons=demon_spam
                    )


            affordable_towers = []
            for t_type in ["crossbow", "cannon", "minigun", "church"]:
                t_cost = get_tower_price(game_state, team, t_type)
                if money >= t_cost + 10:
                    affordable_towers.append(t_type)

            if affordable_towers and build_spaces:
                best_score = -999999
                best_option = None

                for t_type in affordable_towers:
                    for (bx, by) in build_spaces:
                        score = score_tower_placement(bx, by, game_state, team, t_type, lanes)
                        if score > best_score:
                            best_score = score
                            best_option = (t_type, bx, by)

                if best_option:
                    t_type, x, y = best_option
                    return AIAction(
                        "build", x, x, t_type,
                        merc_direction=direction,
                        provoke_demons=demon_spam
                    )

            return AIAction(
                "nothing", 0, 0,
                merc_direction=direction,
                provoke_demons=demon_spam
            )

#Early Game Retaliation
        if 5 < self.turn < 20 and money >= 10:
            for lane in lanes:
                direction = lane.spawn_direction
                if direction not in self.lane_memory:
                    continue

                mem = self.lane_memory[direction]

                is_new_threat = (
                    (len(lane.enemy_mercs) > 0) or
                    (len(lane.demons) > 0) or
                    lane.being_attacked
                )

                if is_new_threat and not mem["early_merc_sent"]:
                    mem["early_merc_sent"] = True
                    if money - house_price >= 10 and build_spaces:
                        spot = choose_house_spot(game_state, team)
                        if spot is not None:
                            x, y = spot
                            return AIAction(
                                "build", x, y, "house",
                                merc_direction=direction,
                                provoke_demons=demon_spam
                            )
                    if direction in merc_dirs:
                        return AIAction(
                            "nothing", 0, 0,
                            merc_direction=direction,
                            provoke_demons=demon_spam
                        )

#Place houses
        if self.turn <= 1 and build_spaces:
            action = build_house(game_state, self.team_color)
            if action:
                return action

        if self.turn < 20 and money >= house_price and build_spaces:
            action = build_house(game_state, self.team_color)
            if action:
                return action
            return AIAction("nothing", 0, 0)
            

#Make Money
        if (best_defense_lane is not None and best_attack_lane is not None and
            best_defense_lane.threat_score < 75 and
            best_attack_lane.pressure_score < 75 and
            money > house_price and build_spaces):

            direction = best_defense_lane.spawn_direction
            spot = choose_house_spot(game_state, team)
            if spot is not None:
                x, y = spot
                if money - house_price >= 10 and direction in merc_dirs:
                    return AIAction(
                        "build", x, y, "house",
                        merc_direction=direction,
                        provoke_demons=demon_spam
                    )
                return AIAction("build", x, y, "house", provoke_demons=demon_spam)

        if tower_choice is None:
            if best_attack_lane is not None and best_attack_lane.pressure_score >= 0:
                direction = best_attack_lane.spawn_direction
                if direction in merc_dirs and money >= 10:
                    return AIAction(
                        "nothing", 0, 0,
                        merc_direction=direction,
                        provoke_demons=demon_spam
                    )
            return AIAction("nothing", 0, 0, provoke_demons=demon_spam)

        tower_type, x, y = tower_choice

#Destroy Houses if Full
        if money > 500 and not build_spaces:
            spot = get_bad_house(game_state, team)
            if spot is not None:
                x, y = spot
                if best_defense_lane is not None:
                    direction = best_defense_lane.spawn_direction
                    return AIAction("destroy", x, y, merc_direction=direction, provoke_demons=demon_spam)
                if best_attack_lane is not None:
                    direction = best_attack_lane.spawn_direction
                    return AIAction("destroy", x, y, merc_direction=direction, provoke_demons=demon_spam)
                return AIAction("destroy", x, y)


#Prioritize Defence
        if (best_defense_lane is not None and best_attack_lane is not None and
            best_defense_lane.threat_score > best_attack_lane.pressure_score and
            best_defense_lane.threat_score >= 50):

            spawn_lane = best_defense_lane
            direction = spawn_lane.spawn_direction
            if build_spaces:
                if afford_merc_and_tower(game_state, team, tower_type, money) and direction in merc_dirs:
                    return AIAction(
                        "build", x, y, tower_type,
                        merc_direction=direction,
                        provoke_demons=demon_spam
                    )
                return AIAction("build", x, y, tower_type)

#Attack 1 lane
        if best_attack_lane is not None and self.turn >= 20:
            spawn_lane = best_attack_lane
            direction = spawn_lane.spawn_direction
            if build_spaces:
                if afford_merc_and_tower(game_state, team, tower_type, money) and direction in merc_dirs:
                    return AIAction(
                        "build", x, y, tower_type,
                        merc_direction=direction,
                        provoke_demons=demon_spam
                    )
            if money >= 10 and direction in merc_dirs:
                return AIAction(
                    "nothing", 0, 0,
                    merc_direction=direction,
                    provoke_demons=demon_spam
                )


        # Fallback
        if money >= 10 and self.turn >=20 and merc_dirs:
            if best_defense_lane is not None:
                direction = best_defense_lane.spawn_direction
                if direction in merc_dirs:
                    return AIAction(
                        "nothing", 0, 0,
                        merc_direction=direction,
                        provoke_demons=demon_spam
                    )
            
            return AIAction(
                "nothing", 0, 0,
                merc_direction=random.choice(merc_dirs),
                provoke_demons=demon_spam
            )
            

        return AIAction("nothing", 0, 0, provoke_demons=demon_spam)
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