import sys
import json

import random # Not necessary to function

# Code required to get the gamestate, 
# it takes the filepath and opens the file
# then it saves it into a gamestate dict that you can use
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as inp:
        game_state : dict = json.load(inp)

action = "build" 
# n/a isn't a valid command, whenever you do something invalid it doesn't do anything
# what_to_build = ['crossbow', 'house', 'cannon', 'minigun', "n/a"]
what_to_build = ['crossbow', "n/a"]
tilegrid = game_state["TileGrid"]

if game_state["CurrentPhase"] == "tower build":
    print(action, random.randint(0,22), random.randint(0,10), random.choice(what_to_build))
elif game_state["CurrentPhase"] == "mercs buy":
    match random.randint(0,1):
        case 0:
            print("queue", 0, 0, "up") 
        case 1:
            print("queue", 0, 0, "down") 
        # case 2:
        #     print("queue", 0, 0, "right")