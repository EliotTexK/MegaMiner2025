import sys
import json
import string

import random # Not necessary to function


# For your convenience:
class AIAction():
    def __init__(
        self,
        x : int,
        y : int,
        tower_to_build : str = '',
        buy_tower : bool = False,
        destroy_tower : bool = False,
        queue_mercenary : bool = False,
        queue_direction : str = ''
    ):
        self.buy_tower_action = buy_tower
        self.destroy_tower_action = destroy_tower
        self.queue_merc_action = queue_mercenary
        self.x = x
        self.y = y
        self.tower_to_build = tower_to_build.strip() # strip get's rid of any excess spaces
        self.queue_direction = queue_direction.strip()
    
    def __str__(self):
        action_string = ""
        support_string = ""
        if self.buy_tower_action:
            action_string = "Build"
            support_string = self.tower_to_build
        elif self.destroy_tower_action:
            action_string = "Destroy"
        elif self.queue_merc_action:
            action_string = "Buy Mercenary"
            support_string = self.queue_direction

        return f"AI Action: {action_string}, Coords: ({self.x},{self.y}), Supported Action: {support_string}"


# Your code should be written inside this class
class Agent:
    def initialize_and_set_name(self, initial_game_state: dict, team_color: str) -> str:
        # Do setup stuff here then return a string representing you team's name
        return "Agent" + ''.join(random.choices(string.ascii_uppercase,k=5))
    
    def do_turn(self, game_state: dict) -> AIAction:
        return AIAction(
            x=0,
            y=0
        )


# Competitors: DO NOT mess with any code below this line!
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
    print(str(agent.do_turn(game_state_init)))

    # loop until the game is over
    while True:
        # get this turn's state
        input_buffer = [input()]
        while input_buffer[-1] != "--END OF TURN--":
            input_buffer.append(input())
        game_state_this_turn = json.loads(''.join(input_buffer[:-1]))

        # get agent action, then send it to the game server
        print(str(agent.do_turn(game_state_this_turn)))