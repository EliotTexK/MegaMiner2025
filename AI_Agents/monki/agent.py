#!/usr/bin/env python3
import sys
import json
import random
from typing import List, Tuple, Dict

# -----------------------
# Action class
# -----------------------
class AIAction:
    def __init__(self, action: str, x: int, y: int, tower_type: str = "", merc_direction: str = "", provoke_demons: bool = False):
        self.action = action.lower().strip()
        self.x = int(x)
        self.y = int(y)
        self.tower_type = tower_type.strip()
        self.merc_direction = merc_direction.upper().strip()
        self.provoke_demons = bool(provoke_demons)

    def to_dict(self):
        return {
            "action": self.action,
            "x": self.x,
            "y": self.y,
            "tower_type": self.tower_type,
            "merc_direction": self.merc_direction,
            "provoke_demons": self.provoke_demons
        }

    def to_json(self):
        return json.dumps(self.to_dict())


# -----------------------
# Helper functions
# -----------------------
def is_out_of_bounds(state: dict, x: int, y: int) -> bool:
    tiles = state.get("FloorTiles", [])
    if not tiles or not isinstance(tiles, list):
        return True
    height = len(tiles)
    width = len(tiles[0]) if height > 0 else 0
    return x < 0 or x >= width or y < 0 or y >= height

def manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def get_available_queue_directions(state: dict, team_color: str) -> List[str]:
    result = []
    offsets = { (0,-1): "N", (0,1): "S", (1,0): "E", (-1,0): "W" }
    player = state.get("PlayerBaseR") if team_color == 'r' else state.get("PlayerBaseB")
    floor = state.get("FloorTiles", [])
    if not player or not floor:
        return result
    for (dx,dy), letter in offsets.items():
        tx = player.get("x", 0) + dx
        ty = player.get("y", 0) + dy
        if not is_out_of_bounds(state, tx, ty):
            try:
                if floor[ty][tx] == "O":
                    result.append(letter)
            except Exception:
                continue
    return result

def get_available_build_spaces(state: dict, team_color: str) -> List[Tuple[int,int]]:
    result = []
    floor = state.get("FloorTiles", [])
    entity = state.get("EntityGrid", [])
    if not floor or not entity:
        return result
    for y, row in enumerate(floor):
        for x, ch in enumerate(row):
            try:
                if ch == team_color and entity[y][x] == "":
                    result.append((x,y))
            except Exception:
                continue
    return result

def get_my_towers(state: dict, team_color: str) -> List[dict]:
    res = []
    towers = state.get("Towers", [])
    if not isinstance(towers, list):
        return res
    for t in towers:
        try:
            if t.get("Team") == team_color:
                res.append(t)
        except Exception:
            continue
    return res

def get_my_money_amount(state: dict, team_color: str) -> int:
    try:
        return int(state.get("RedTeamMoney", 0)) if team_color == 'r' else int(state.get("BlueTeamMoney", 0))
    except Exception:
        return 0

def pick_front_spot(spaces: List[Tuple[int,int]], state: dict, team_color: str) -> Tuple[int,int]:
    if not spaces:
        return (0,0)
    # chooses spot closest to enemy base (legacy behavior)
    enemy = state.get("PlayerBaseB") if team_color == 'r' else state.get("PlayerBaseR")
    if not enemy:
        return random.choice(spaces)
    return min(spaces, key=lambda p: manhattan(p, (enemy["x"], enemy["y"])))

def pick_back_spot(spaces: List[Tuple[int,int]], state: dict, team_color: str) -> Tuple[int,int]:
    if not spaces:
        return (0,0)
    enemy = state.get("PlayerBaseB") if team_color == 'r' else state.get("PlayerBaseR")
    my_base = state.get("PlayerBaseR") if team_color == 'r' else state.get("PlayerBaseB")
    if not enemy or not my_base:
        return random.choice(spaces)
    def score(p):
        return 3 * manhattan(p, (enemy["x"], enemy["y"])) - 1 * manhattan(p, (my_base["x"], my_base["y"]))
    return max(spaces, key=score)


# -----------------------
# Agent
# -----------------------
class Agent:
    def initialize_and_set_name(self, initial_game_state: dict, team_color: str) -> str:
        self.team_color = team_color
        self.crossbow_built = False
        self.crossbow_built_turn = -1
        self.crossbow_x = -1
        self.crossbow_y = -1
        self.house_count = 0
        self.church_count = 0
        self.minigun_count = 0

        # merc accounting
        self.lane_mercs: Dict[str,float] = {"N":0,"S":0,"E":0,"W":0}
        self.decay_per_turn = 0.05

        # defense cycle state
        self.defense_cycle = 0  # 0,1,2 = mercs; 3 = minigun

        # house/church timing
        self.last_church_turn = -15
        self.last_house_turn = -16

        # new: max-out after 3 houses
        self.max_per_lane = 3
        self.maxed_after_three_houses = False

        return "Monki"

    def decay_lane_counts(self):
        for d in self.lane_mercs:
            self.lane_mercs[d] = max(0.0, self.lane_mercs[d] - self.decay_per_turn)

    def choose_lane_for_merc(self, state: dict) -> str:
        dirs = get_available_queue_directions(state, self.team_color)
        if not dirs:
            return ""
        # choose lane with fewest queued mercs (spread evenly)
        return min(dirs, key=lambda d: self.lane_mercs.get(d, 0))

    def all_lanes_maxed(self, state: dict) -> bool:
        dirs = get_available_queue_directions(state, self.team_color)
        if not dirs:
            return True
        for d in dirs:
            if self.lane_mercs.get(d, 0) < float(self.max_per_lane):
                return False
        return True

    def do_turn(self, state: dict) -> AIAction:
        try:
            self.decay_lane_counts()
            turn = int(state.get("CurrentTurn",0))
            money = get_my_money_amount(state, self.team_color)
            build_spaces = get_available_build_spaces(state, self.team_color)
            q_dirs = get_available_queue_directions(state, self.team_color)
            towers = get_my_towers(state, self.team_color)

            # count towers
            self.house_count = sum(1 for t in towers if str(t.get("Type","")).lower() == "house")
            self.church_count = sum(1 for t in towers if str(t.get("Type","")).lower() == "church")
            self.minigun_count = sum(1 for t in towers if str(t.get("Type","")).lower() == "minigun")

            # Destroy crossbow after 30 rounds
            if self.crossbow_built and self.crossbow_built_turn >= 0 and turn - self.crossbow_built_turn >= 30:
                if self.crossbow_x >= 0 and self.crossbow_y >= 0:
                    self.crossbow_built = False  # Mark as destroyed so we don't try again
                    return AIAction("destroy", self.crossbow_x, self.crossbow_y)

            # --- NEW: If we have 3 houses and haven't maxed yet -> start maxing mercs ---
            if self.house_count >= 3 and not self.maxed_after_three_houses:
                # If there are no available queue dirs, we can't spawn mercs; skip this phase but don't mark done
                if q_dirs and money >= 30:
                    # find a lane that isn't maxed yet (and is available)
                    candidate_lanes = [d for d in q_dirs if self.lane_mercs.get(d, 0) < float(self.max_per_lane)]
                    if candidate_lanes:
                        lane = min(candidate_lanes, key=lambda d: self.lane_mercs.get(d, 0))
                        # spawn one merc this turn into that lane
                        self.lane_mercs[lane] = self.lane_mercs.get(lane, 0) + 1.0
                        return AIAction("nothing", 0, 0, merc_direction=lane)
                    else:
                        # all available lanes are already at per-lane cap -> mark as done
                        self.maxed_after_three_houses = True
                        # fall through to normal logic this turn (no action used)
                else:
                    # not enough money or no queue dirs: wait and attempt next turn (don't mark done)
                    # but if absolutely no money and no build option, just proceed to normal logic
                    pass

            # ----------------------------------------------------
            # EARLY game: build houses up to 3 (if we haven't reached 3 and it's worth building)
            # ----------------------------------------------------
            if self.house_count < 3 and money >= 20 and build_spaces:
                loc = pick_back_spot(build_spaces, state, self.team_color)
                return AIAction("build", loc[0], loc[1], "house")

            # build 1 crossbow early if not yet built
            if not self.crossbow_built and money >= 20 and build_spaces:
                loc = pick_front_spot(build_spaces, state, self.team_color)
                self.crossbow_built = True
                self.crossbow_built_turn = turn
                self.crossbow_x = loc[0]
                self.crossbow_y = loc[1]
                return AIAction("build", loc[0], loc[1], "crossbow")

            # ----------------------------------------------------
            # Build house every 16 turns max (if desired)
            # ----------------------------------------------------
            if turn - self.last_house_turn >= 16 and money >= 20 and build_spaces:
                loc = pick_back_spot(build_spaces, state, self.team_color)
                self.last_house_turn = turn
                return AIAction("build", loc[0], loc[1], "house")

            # ----------------------------------------------------
            # Mid/Late Game: Defense Cycle, Churches every 15 turns
            # ----------------------------------------------------
            action = None

            # Churches every 15 turns max
            if turn - self.last_church_turn >= 15 and money >= 20 and build_spaces:
                loc = pick_back_spot(build_spaces, state, self.team_color)
                self.last_church_turn = turn
                action = AIAction("build", loc[0], loc[1], "church")
            else:
                # Defensive cycle: 3 mercs then 1 minigun
                if self.defense_cycle < 3 and q_dirs and money >= 30:
                    lane = self.choose_lane_for_merc(state)
                    if lane:
                        self.lane_mercs[lane] = self.lane_mercs.get(lane, 0) + 1.0
                        action = AIAction("nothing",0,0,merc_direction=lane)
                        self.defense_cycle +=1
                elif self.defense_cycle == 3 and money >= 60 and build_spaces:
                    loc = pick_front_spot(build_spaces, state, self.team_color)
                    action = AIAction("build", loc[0], loc[1], "minigun")
                    self.defense_cycle = 0
                else:
                    # fallback: spawn mercs if money allows
                    if q_dirs and money >= 30:
                        lane = self.choose_lane_for_merc(state)
                        if lane:
                            self.lane_mercs[lane] = self.lane_mercs.get(lane, 0) + 1.0
                            action = AIAction("nothing",0,0,merc_direction=lane)

            # fallback nothing
            if not action:
                action = AIAction("nothing",0,0)

            return action

        except Exception as e:
            print(f"[AI ERROR] {e}", file=sys.stderr)
            return AIAction("nothing",0,0)


# -----------------------
# DRIVER
# -----------------------
if __name__ == '__main__':
    try:
        team_color = 'r' if input() == "--YOU ARE RED--" else 'b'
    except Exception:
        team_color = 'r'

    input_buffer = [input()]
    while input_buffer[-1] != "--END INITIAL GAME STATE--":
        input_buffer.append(input())
    try:
        game_state_init = json.loads(''.join(input_buffer[:-1]))
    except Exception:
        game_state_init = {}

    agent = Agent()
    print(agent.initialize_and_set_name(game_state_init, team_color))

    try:
        print(agent.do_turn(game_state_init).to_json())
    except Exception:
        print(AIAction("nothing",0,0).to_json())

    while True:
        try:
            input_buffer = [input()]
            while input_buffer[-1] != "--END OF TURN--":
                input_buffer.append(input())
            try:
                game_state_this_turn = json.loads(''.join(input_buffer[:-1]))
            except Exception:
                game_state_this_turn = {}
            print(agent.do_turn(game_state_this_turn).to_json())
        except Exception:
            try:
                print(AIAction("nothing",0,0).to_json())
            except Exception:
                pass
            break