import sys
import pickle
from Game import Game
from pathlib import Path

game = Game()

can_start : bool = False

## Tries to find two ai files if there is no arguments supplied
def find_files_by_pattern(pattern, search_path):
    search_path_obj = Path(search_path)
    matched_files = list(search_path_obj.rglob(pattern))
    return matched_files

default_search_dir = 'C:/MegaMiner/MegaMiner2025/backend/AI_Agents'
file_pattern = "*.py"


## First check if there are no arguments supplied with the program
if len(sys.argv) <= 1: ## for python code the path to the file is an argument supplied, so there will always be 1 system arg
    files_found = find_files_by_pattern(file_pattern, default_search_dir)
    #print(files_found)
    if len(files_found) >= 2 :
        print(f"Found and using files '{files_found[0]}' and '{files_found[1]}'")
        game.load_ai_paths(files_found[0], files_found[1])
        can_start = True
    else:
        print("Not enough AI Files supplied!")
else:  ## code was called with two  or more arguments supplied, this could be either the two AI_files used, or it could be the visualizer callig for a turn

    if sys.argv[1] == "-v": ## visulizer called it
        
        if len(sys.argv) > 2 and sys.argv[2] == "initial":
            
            print(game.game_state_to_json()) ##Gives visualizer the initial game_state
            with open('C:/MegaMiner/MegaMiner2025/backend/game_state.pkl', 'wb') as outp:
                pickle.dump(game.game_state, outp, pickle.HIGHEST_PROTOCOL)



        else: ## The json string will always end with an } 

            files_found = find_files_by_pattern(file_pattern, default_search_dir)
            game.load_ai_paths(files_found[0], files_found[1])

            with open('C:/MegaMiner/MegaMiner2025/backend/game_state.pkl', 'rb') as inp:
                game.game_state = pickle.load(inp)

            game.run_turn() ## runs a turn with supplied game_state
            print(game.game_state_to_json()) ##Gives next state to viz

            with open('C:/MegaMiner/MegaMiner2025/backend/game_state.pkl', 'wb') as outp:
                pickle.dump(game.game_state, outp, pickle.HIGHEST_PROTOCOL)

if can_start:
    while game.game_state.turns_progressed < 1000:
        game.run_turn()
    print("Finished")


    