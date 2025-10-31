from Game import Game
import os
import pickle
import argparse
from pathlib import Path

game = Game()

current_file_path = Path(__file__).parent.resolve() # Gets the parent directory
dataPath = str(current_file_path) + "/data/backenddata.pkl" # Makes sure the data path is relative to main.py

if __name__ == "__main__":
    # Using arg parse to parse argument data
    parser = argparse.ArgumentParser(description='Backend for ApocaWarlord.',
                                    epilog='Example usage: python main.py "PathToAI" "PathToAI"')

    # Adding arguments
    parser.add_argument('ai_file_one', default="", help='The path to AI agent 1')
    parser.add_argument('ai_file_two', default="", help='The path to AI agent 2')

    parser.add_argument('-v','--vizulizer', action='store_true',
                        help='Called by the Vizulizer, if called the program will do one game turn instead of 1000')
    parser.add_argument('-i', '--initial',action='store_true', help='Called by the vizuliser to determine whether or not it\'s the first turn')
    args = parser.parse_args()

    # Uses relative paths
    game.load_ai_paths(args.ai_file_one, args.ai_file_two)
    
    # Visualizer mode
    if args.vizulizer:
        # First turn?
        if args.initial:
            # Initialize the game
            game.make_blank_game()
            print(game.game_json_file_path) # Gives next state to viz

            with open(dataPath, 'wb') as outp:
                pickle.dump(game.game_state, outp, pickle.HIGHEST_PROTOCOL)
        else:
            # Turn other than first turn
            with open(dataPath, 'rb') as inp:
                game.game_state = pickle.load(inp)

            game.run_turn() # runs a turn with supplied game_state

            print(game.game_json_file_path)
            
            with open(dataPath, 'wb') as outp:
                pickle.dump(game.game_state, outp, pickle.HIGHEST_PROTOCOL)
    # Non-visualizer mode
    else:        
        # Game playing with two AI's provided

        dot = 1
        while game.game_state.turns_progressed < 1000 and game.game_state.victory == None:
            dot += 1
            if dot > 3: dot = 1
            if os.name == 'nt':
                _ = os.system('cls')
            # For macOS and Linux
            else:
                _ = os.system('clear')

            match dot:
                case 1:
                    print("Running Game.   ", "Turns Progressed: ", game.game_state.turns_progressed)
                case 2:
                    print("Running Game..  ", "Turns Progressed: ", game.game_state.turns_progressed)
                case 3:
                    print("Running Game... ", "Turns Progressed: ", game.game_state.turns_progressed)
                
            game.run_turn()
        print("Finished")


    