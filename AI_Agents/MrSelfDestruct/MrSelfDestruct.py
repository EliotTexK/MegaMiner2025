import sys
import json
import random
from typing import Optional, Tuple, List


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
    """

    def __init__(
        self,
        action: str,
        x: int,
        y: int,
        tower_type: str = "",
        merc_direction: str = "",
        provoke_demons: bool = False,
    ):
        self.action = action.lower().strip()
        self.x = x
        self.y = y
        self.tower_type = tower_type.strip()
        self.merc_direction = merc_direction.upper().strip()
        self.provoke_demons = provoke_demons

    def to_dict(self):
        return {
            "action": self.action,
            "x": self.x,
            "y": self.y,
            "tower_type": self.tower_type,
            "merc_direction": self.merc_direction,
            "provoke_demons": self.provoke_demons,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


# ----------------------------------------------------
# Helper functions from the template
# ----------------------------------------------------

def is_out_of_bounds(game_state: dict, x: int, y: int) -> bool:
    return (
        x < 0
        or x >= len(game_state["FloorTiles"][0])
        or y < 0
        or y >= len(game_state["FloorTiles"])
    )


def get_available_queue_directions(game_state: dict, team_color: str) -> list:
    result = []
    offsets = {
        (0, -1): "N",
        (0, 1): "S",
        (1, 0): "E",
        (-1, 0): "W",
    }

    player = game_state["PlayerBaseR"] if team_color == "r" else game_state["PlayerBaseB"]
    for (dx, dy), d_str in offsets.items():
        tx = player["x"] + dx
        ty = player["y"] + dy
        if (
            not is_out_of_bounds(game_state, tx, ty)
            and game_state["FloorTiles"][ty][tx] == "O"
        ):
            result.append(d_str)
    return result


def get_available_build_spaces(game_state: dict, team_color: str):
    result = []
    for y, row in enumerate(game_state["FloorTiles"]):
        for x, ch in enumerate(row):
            if ch == team_color and game_state["EntityGrid"][y][x] == "":
                result.append((x, y))
    return result


def get_my_towers(game_state: dict, team_color: str):
    result = []
    for tower in game_state["Towers"]:
        if tower["Team"] == team_color:
            result.append(tower)
    return result


def get_my_money_amount(game_state: dict, team_color: str) -> int:
    return game_state["RedTeamMoney"] if team_color == "r" else game_state["BlueTeamMoney"]


# ----------------------------------------------------
# Greedy DemonRush Agent (with merc bank & merc-train defense)
# ----------------------------------------------------

class Agent:
    def initialize_and_set_name(self, initial_game_state: dict, team_color: str) -> str:
        self.team_color = team_color
        self.enemy_color = "b" if team_color == "r" else "r"
        self.my_base_key = "PlayerBaseR" if team_color == "r" else "PlayerBaseB"
        self.opp_base_key = "PlayerBaseB" if team_color == "r" else "PlayerBaseR"

        # Demon spawners
        self.demon_spawners = [
            (sp["x"], sp["y"]) for sp in initial_game_state.get("DemonSpawners", [])
        ]

        self.turn_index = 0
        self.phase = "rush"

        # Cache base positions
        my_base = initial_game_state[self.my_base_key]
        opp_base = initial_game_state[self.opp_base_key]
        self.my_base_pos = (my_base["x"], my_base["y"])
        self.opp_base_pos = (opp_base["x"], opp_base["y"])

        # Short base-to-base heuristic (for maps like 4/6)
        base_dist = self._manhattan(
            self.my_base_pos[0],
            self.my_base_pos[1],
            self.opp_base_pos[0],
            self.opp_base_pos[1],
        )
        self.short_map = base_dist <= 8 and bool(self.demon_spawners)

        # Approximate tower range (used for placement heuristics)
        self.APPROX_TOWER_RANGE = 3

        return "Mr. Self Destruct"

    # ---------- geometry / utility ----------

    def _manhattan(self, x1, y1, x2, y2) -> int:
        return abs(x1 - x2) + abs(y1 - y2)

    def _distance_to_nearest_spawner(self, x: int, y: int) -> int:
        if not self.demon_spawners:
            return 999999
        return min(self._manhattan(x, y, sx, sy) for (sx, sy) in self.demon_spawners)

    def _choose_defense_tile_near_spawner(self, build_spaces):
        if not build_spaces:
            return None
        return min(
            build_spaces,
            key=lambda xy: self._distance_to_nearest_spawner(xy[0], xy[1]),
        )

    def _choose_safe_house_tile(self, game_state, build_spaces):
        if not build_spaces:
            return None
        if not self.demon_spawners:
            return random.choice(build_spaces)
        # farthest from spawners
        return max(
            build_spaces,
            key=lambda xy: self._distance_to_nearest_spawner(xy[0], xy[1]),
        )

    def _get_tower_counts(self, game_state):
        my_towers = get_my_towers(game_state, self.team_color)
        counts = {"House": 0, "Cannon": 0, "Crossbow": 0, "Minigun": 0, "Church": 0}
        for t in my_towers:
            ttype = t.get("Type")
            if ttype in counts:
                counts[ttype] += 1
        return counts

    def _compute_demon_threat(self, game_state) -> Tuple[int, int]:
        my_base = game_state[self.my_base_key]
        opp_base = game_state[self.opp_base_key]

        my_threat = 0
        opp_threat = 0
        for dem in game_state["Demons"]:
            target_team = dem["Team"]  # demon attacks this team
            if target_team == self.team_color:
                if self._manhattan(dem["x"], dem["y"], my_base["x"], my_base["y"]) <= 6:
                    my_threat += 1
            else:
                if self._manhattan(dem["x"], dem["y"], opp_base["x"], opp_base["y"]) <= 6:
                    opp_threat += 1
        return my_threat, opp_threat

    def _nearest_enemy_merc_to_base(self, game_state) -> Tuple[Optional[dict], int]:
        my_base = game_state[self.my_base_key]
        best = None
        best_dist = 999999
        for m in game_state["Mercenaries"]:
            if m["Team"] == self.enemy_color:
                d = self._manhattan(m["x"], m["y"], my_base["x"], my_base["y"])
                if d < best_dist:
                    best_dist = d
                    best = m
        return best, best_dist

    def _nearest_hostile_demon_to_base(self, game_state) -> Tuple[Optional[dict], int]:
        """
        Demons have Team = the team they are targeting.
        So demons with Team == self.team_color are hostile to us.
        """
        my_base = game_state[self.my_base_key]
        best = None
        best_dist = 999999
        for d in game_state["Demons"]:
            if d["Team"] == self.team_color:
                dist = self._manhattan(d["x"], d["y"], my_base["x"], my_base["y"])
                if dist < best_dist:
                    best_dist = dist
                    best = d
        return best, best_dist

    def _direction_from_base_to_point(self, game_state, x: int, y: int) -> Optional[str]:
        base = game_state[self.my_base_key]
        dx = x - base["x"]
        dy = y - base["y"]
        if dx == 0 and dy == 0:
            return None
        if abs(dx) >= abs(dy):
            return "E" if dx > 0 else "W"
        else:
            return "S" if dy > 0 else "N"

    def _have_friendly_merc_in_direction(self, game_state, direction: str) -> bool:
        base = game_state[self.my_base_key]
        for m in game_state["Mercenaries"]:
            if m["Team"] != self.team_color:
                continue
            d = self._direction_from_base_to_point(game_state, m["x"], m["y"])
            if d == direction:
                return True
        return False

    def _pick_best_attack_directions(self, game_state, q_dirs: List[str]) -> List[str]:
        if not q_dirs:
            return []
        my_base = game_state[self.my_base_key]
        opp_base = game_state[self.opp_base_key]
        dx = opp_base["x"] - my_base["x"]
        dy = opp_base["y"] - my_base["y"]

        if abs(dx) >= abs(dy):
            primary = "E" if dx > 0 else "W"
            secondary = "S" if dy > 0 else "N"
        else:
            primary = "S" if dy > 0 else "N"
            secondary = "E" if dx > 0 else "W"

        result = []
        if primary in q_dirs:
            result.append(primary)
        if secondary in q_dirs and secondary not in result:
            result.append(secondary)
        for d in sorted(q_dirs):
            if d not in result:
                result.append(d)
        return result[:2]

    # ---------- base-under-siege heuristic ----------

    def _base_under_siege(
        self,
        my_hp: int,
        nearest_merc_dist: int,
        nearest_demon_dist: int,
    ) -> bool:
        """
        True if base is lowish HP AND something is basically on top of us.
        """
        lowish_hp = my_hp <= 60

        merc_siege = nearest_merc_dist <= 1  # already at or adjacent to base
        demon_siege = nearest_demon_dist <= 2  # demons chunk and keep walking

        return lowish_hp and (merc_siege or demon_siege)

    # ---------- choose defense tile that covers threat path & base ----------

    def _choose_defense_tile_for_threat_path(
        self,
        game_state: dict,
        build_spaces: List[Tuple[int, int]],
        threat_unit: dict,
        approx_range: int = 3,
    ) -> Optional[Tuple[int, int]]:
        """
        Try to put a tower so that:
          - The threat will be in range at some point while walking from threat -> base, AND
          - The base tile itself is (ideally) within range.
        """
        if not build_spaces or threat_unit is None:
            return None

        base = game_state[self.my_base_key]
        bx, by = base["x"], base["y"]
        tx, ty = threat_unit["x"], threat_unit["y"]

        dx = bx - tx
        dy = by - ty
        steps = max(abs(dx), abs(dy), 1)

        path_points = []
        for i in range(steps + 1):
            x = tx + round(dx * i / steps)
            y = ty + round(dy * i / steps)
            path_points.append((x, y))

        def dist_to_path(px, py):
            return min(self._manhattan(px, py, x, y) for (x, y) in path_points)

        # Tiles that hit BOTH base tile and threat tile
        dual_coverage_candidates = []
        for (x, y) in build_spaces:
            db = self._manhattan(x, y, bx, by)
            dt = self._manhattan(x, y, tx, ty)
            if db <= approx_range and dt <= approx_range:
                dual_coverage_candidates.append((x, y))

        if dual_coverage_candidates:
            best_tile = None
            best_score = 999999
            for (x, y) in dual_coverage_candidates:
                score = dist_to_path(x, y)
                if score < best_score:
                    best_score = score
                    best_tile = (x, y)
            return best_tile

        # Fallback: close to path and prefer covering base tile if possible
        best_tile = None
        best_score = 999999
        for (x, y) in build_spaces:
            d_path = dist_to_path(x, y)
            d_base = self._manhattan(x, y, bx, by)
            score = d_path + d_base
            if d_base > approx_range:
                score += 50  # heavy penalty if can't see base
            if score < best_score:
                best_score = score
                best_tile = (x, y)

        return best_tile

    # ---------- phase control ----------

    def _update_phase(self, turn: int, num_houses: int):
        # Rush only turns 0–4; after that we care about eco.
        if turn <= 4:
            self.phase = "rush"
        else:
            if num_houses < 2:
                self.phase = "force_second_house"
            else:
                self.phase = "stabilize"

    # ---------- main turn ----------

    def do_turn(self, game_state: dict) -> AIAction:
        self.turn_index += 1
        turn = self.turn_index

        money = get_my_money_amount(game_state, self.team_color)
        build_spaces = get_available_build_spaces(game_state, self.team_color)
        q_dirs = get_available_queue_directions(game_state, self.team_color)

        my_base = game_state[self.my_base_key]
        opp_base = game_state[self.opp_base_key]
        my_hp = my_base["Health"]
        opp_hp = opp_base["Health"]

        tower_counts = self._get_tower_counts(game_state)
        num_houses = tower_counts["House"]
        num_miniguns = tower_counts["Minigun"]
        num_crossbows = tower_counts["Crossbow"]
        num_cannons = tower_counts["Cannon"]

        my_demon_threat, opp_demon_threat = self._compute_demon_threat(game_state)
        nearest_merc, nearest_merc_dist = self._nearest_enemy_merc_to_base(game_state)
        nearest_demon, nearest_demon_dist = self._nearest_hostile_demon_to_base(game_state)

        prices = (
            game_state["TowerPricesR"]
            if self.team_color == "r"
            else game_state["TowerPricesB"]
        )
        house_price = prices["House"]
        crossbow_price = prices["Crossbow"]
        minigun_price = prices["Minigun"]
        cannon_price = prices["Cannon"]

        MERC_COST = 10
        MERC_EMERGENCY_BANK = 10
        RUSH_TURNS = 4
        MAX_DEF_THREAT_RANGE = 8
        CONGA_RANGE = 7  # when conga-line is close enough that towers won't save us

        under_siege = self._base_under_siege(
            my_hp, nearest_merc_dist, nearest_demon_dist
        )

        has_visible_threat = (
            (nearest_merc is not None and nearest_merc_dist <= MAX_DEF_THREAT_RANGE)
            or (nearest_demon is not None and nearest_demon_dist <= MAX_DEF_THREAT_RANGE)
        )

        # Update phase
        self._update_phase(turn, num_houses)

        # Choose main threat (enemy merc or hostile demon) closest to our base
        threat_unit = None
        threat_dist = 999999
        if nearest_merc is not None:
            threat_unit = nearest_merc
            threat_dist = nearest_merc_dist
        if nearest_demon is not None and nearest_demon_dist < threat_dist:
            threat_unit = nearest_demon
            threat_dist = nearest_demon_dist

        # ------------ emergency bank policy & merc-train ------------

        def have_emergency_bank() -> bool:
            # Only keep an emergency bank once we have at least TWO houses.
            return num_houses >= 2

        # If we have 2+ houses and a conga-line is within CONGA_RANGE,
        # we stop building towers/houses this turn and save gold for mercs.
        need_merc_train = (
            num_houses >= 2
            and threat_unit is not None
            and threat_dist <= CONGA_RANGE
        )

        def can_spend_on_tower(cost: int) -> bool:
            """
            If we have an emergency bank (2+ houses) and there's a visible threat,
            tower spending must preserve it. Otherwise spend freely if we have the gold.
            """
            if have_emergency_bank() and has_visible_threat:
                return money - cost >= MERC_EMERGENCY_BANK
            else:
                return money >= cost

        # -----------------------
        # Step 1: decide tower build FIRST
        # -----------------------
        action = "nothing"
        build_x, build_y = 0, 0
        build_type = ""
        tower_cost = 0

        # If we're in "merc train" mode, SKIP all tower/house building.
        if not need_merc_train:

            # Guarantee first house early (ignore merc bank here; early game)
            if (
                action == "nothing"
                and num_houses == 0
                and build_spaces
                and money >= house_price
            ):
                if turn <= 2:
                    spot = self._choose_safe_house_tile(game_state, build_spaces)
                    if spot:
                        build_x, build_y = spot
                        build_type = "house"
                        action = "build"
                        tower_cost = house_price

            # Force a second house: DO NOT reserve an emergency bank before 2 houses.
            if (
                action == "nothing"
                and num_houses < 2
                and build_spaces
                and money >= house_price
                and turn >= 5
                and not under_siege
            ):
                dying_now = (
                    my_hp <= 30
                    and (
                        (nearest_merc is not None and nearest_merc_dist <= 2)
                        or my_demon_threat >= 3
                    )
                )
                if not dying_now:
                    spot = self._choose_safe_house_tile(game_state, build_spaces)
                    if spot:
                        build_x, build_y = spot
                        build_type = "house"
                        action = "build"
                        tower_cost = house_price

            # Third+ house when stabilized and not in immediate danger.
            max_houses_allowed = 3 if self.short_map else 4

            if (
                action == "nothing"
                and self.phase == "stabilize"
                and num_houses < max_houses_allowed
                and build_spaces
                and money >= house_price
                and not under_siege
            ):
                close_merc = nearest_merc is not None and nearest_merc_dist <= 3
                need_bank = have_emergency_bank()
                if not (close_merc and my_hp <= 30):
                    # Respect emergency bank only when we actually have it (2+ houses)
                    if (not need_bank) or (money - house_price >= MERC_EMERGENCY_BANK):
                        spot = self._choose_safe_house_tile(game_state, build_spaces)
                        if spot:
                            build_x, build_y = spot
                            build_type = "house"
                            action = "build"
                            tower_cost = house_price

            # PRIORITY: if under threat and we have at least 1 house, put down a cheap defense tower
            if (
                action == "nothing"
                and build_spaces
                and num_houses >= 1
                and has_visible_threat
            ):
                threat_for_tower = None
                threat_dist_for_tower = 999999

                if nearest_demon is not None and nearest_demon_dist <= MAX_DEF_THREAT_RANGE:
                    threat_for_tower = nearest_demon
                    threat_dist_for_tower = nearest_demon_dist

                if nearest_merc is not None and nearest_merc_dist < threat_dist_for_tower:
                    threat_for_tower = nearest_merc
                    threat_dist_for_tower = nearest_merc_dist

                if threat_for_tower is not None:
                    spot = self._choose_defense_tile_for_threat_path(
                        game_state,
                        build_spaces,
                        threat_for_tower,
                        approx_range=self.APPROX_TOWER_RANGE,
                    )
                else:
                    spot = None

                if spot is not None:
                    # Prefer Cannon to keep costs low when under pressure
                    if can_spend_on_tower(cannon_price):
                        build_x, build_y = spot
                        build_type = "cannon"
                        action = "build"
                        tower_cost = cannon_price
                    elif can_spend_on_tower(crossbow_price):
                        build_x, build_y = spot
                        build_type = "crossbow"
                        action = "build"
                        tower_cost = crossbow_price

            # If stabilized, not under siege, and not in immediate threat, invest in heavier defenses
            if (
                action == "nothing"
                and self.phase == "stabilize"
                and num_houses >= 2
                and build_spaces
                and not has_visible_threat
            ):
                # A couple of miniguns if we can afford them without violating bank (2+ houses)
                if num_miniguns < 2 and can_spend_on_tower(minigun_price):
                    spot = self._choose_defense_tile_near_spawner(build_spaces)
                    if spot:
                        build_x, build_y = spot
                        build_type = "minigun"
                        action = "build"
                        tower_cost = minigun_price
                # Then crossbows for extra DPS
                if (
                    action == "nothing"
                    and can_spend_on_tower(crossbow_price)
                ):
                    spot = self._choose_defense_tile_near_spawner(build_spaces)
                    if spot:
                        build_x, build_y = spot
                        build_type = "crossbow"
                        action = "build"
                        tower_cost = crossbow_price

        # -----------------------
        # Step 2: decide mercenary with REMAINING money
        # -----------------------
        merc_direction = ""
        remaining = money - tower_cost

        # Defensive merc: always allowed to spend down to 0 if needed
        if (
            threat_unit is not None
            and threat_dist <= MAX_DEF_THREAT_RANGE
            and remaining >= MERC_COST
            and q_dirs
        ):
            base = game_state[self.my_base_key]
            bx, by = base["x"], base["y"]
            dir_offsets = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

            best_lane = None
            best_score = 999999
            for d in q_dirs:
                dx, dy = dir_offsets[d]
                spawn_x = bx + dx
                spawn_y = by + dy
                dist_to_threat = self._manhattan(
                    spawn_x, spawn_y, threat_unit["x"], threat_unit["y"]
                )
                if (
                    dist_to_threat < best_score
                    and not self._have_friendly_merc_in_direction(game_state, d)
                ):
                    best_score = dist_to_threat
                    best_lane = d

            if best_lane is not None:
                merc_direction = best_lane

        # Early offensive rush mercs (turns 0–4) if we still haven't set a defensive merc
        if (
            merc_direction == ""
            and self.phase == "rush"
            and turn <= RUSH_TURNS
            and remaining >= MERC_COST
            and q_dirs
        ):
            best_dirs = self._pick_best_attack_directions(game_state, q_dirs)
            if best_dirs:
                merc_direction = best_dirs[0]

        # Extra offensive mercs later:
        # - Before 2 houses: no emergency bank, just need MERC_COST.
        # - At 2+ houses: only if we still keep a full bank.
        if (
            merc_direction == ""
            and self.phase == "stabilize"
            and q_dirs
            and not under_siege
        ):
            if have_emergency_bank():
                if remaining >= MERC_COST + MERC_EMERGENCY_BANK:
                    best_dirs = self._pick_best_attack_directions(game_state, q_dirs)
                    if best_dirs:
                        merc_direction = best_dirs[0]
            else:
                if remaining >= MERC_COST:
                    best_dirs = self._pick_best_attack_directions(game_state, q_dirs)
                    if best_dirs:
                        merc_direction = best_dirs[0]

        # -----------------------
        # Step 3: provoke demons? (still off for stability)
        # -----------------------
        do_provoke = False

        # Return final action
        return AIAction(
            action,
            build_x,
            build_y,
            build_type,
            merc_direction=merc_direction,
            provoke_demons=do_provoke,
        )



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
