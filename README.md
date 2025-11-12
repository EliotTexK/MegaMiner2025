# MegaMiner 2025
MegaMiner is a yearly competition held by Computer Science students at Missouri S&T. Teams of up to 4 people create AI agents to compete in a video game tournament. This year, the game is ApocaWarlords. If you want to make an AI agent, the first thing you need to do is to understand the rules/mechanics of the game. To learn the rules of the game, read the [README.md file in the rules directory of this repository](https://github.com/EliotTexK/MegaMiner2025/tree/main/rules). Then, once you've done that, see the instructions below for creating/testing your agent.

## Installation
1. Clone this repository to get access to maps and the example AI Agents.
2. Install the latest version of Python. The game has been tested on the most recent version, and the tournament itself will also use it.
3. Get the Visualizer executable from our [Releases](https://github.com/EliotTexK/MegaMiner2025/releases). Put it in the Visualizer folder of the repository you just cloned.

## How The Software Works
When it comes to running MegaMiner 2025, whether you are testing your AI, or hosting a competition, there are 4 programs/processes involved:
- The Backend - This is a game server made with Python that runs the core game logic. You can run it using the command-line, or if you're using the Visualizer, the Visualizer will run it for you. It will manage 2 competing AI agents by sending the state of the game to them and recieving their inputs. It will print out a representation of the game state each turn and write to a log file.
- The Visualizer - This is a GUI application which displays the game graphically. It does this by running the Backend and interpreting the game state it prints out.
- The two AI Agents - these are Python files written by competitors. These are meant to be run by the Backend as sub-processes. Each turn, they receive game state from the backend and send back controls ( AI Actions ) for that turn.

## How To Run The Visualizer
Go to the Visualizer folder/directory where you put the executable. Then, double-click it, or run it using the command-line. Click the "Play Game" button. From there, select a map and your AI agents. The Visualizer also allows the game to be playable by humans, and you can select that option. When you're ready to start, press "Go".

## How To Run The Backend ( No Visualizer )
Change directories to `backend`. Run the following command:

`python3 main.py ../maps/your_map.json -a1 ../AI_Agents/your_red_player_ai.py -a2 ../AI_Agents/your_blue_player_ai.py`

But substitute the map and AI agents you want. For example:

`python3 main.py ../maps/map2.json -a1 ../AI_Agents/ExampleAgentRuleBased.py -a2 ../AI_Agents/ExampleAgentRuleBased.py`

## How To Create An Agent
Take a look at `ExampleAgentRuleBased.py` and/or `AgentTemplate.py`. You will be copying the format of those files, and making your own custom version of the `Agent` class. All you need to do is fill out two functions:
1. `initialize_and_set_name` - Gets called at the start of the game, and gives you access to the game's initial state, and importantly, **which team you are on**. Do any initialization you want to here. Return a python string containing your team's name.
2. `do_turn` - Gets called every turn, and has access to the game's state at that turn. This function should return an object of type `AIAction`, representing what you want your agent to do at that turn.
If you want your agent to import libraries or custom python files, or have access to data files (like model weights for deep RL), just let the event organizers know.

## Game State Format
The functions you will be writing for your `Agent` will recieve the state of the game as a big python dictionary. If you *really want to* understand the technical details of how this is created, you can read the driver code at the bottom of `AgentTemplate.py`, and then read through `backend/Game.py` and `backend/GameState.py`. However, knowing these technical details is not necessary.

1. **Victory Condition** - `game_state["Victory"]` - Will be the string `'r'` if the Red player has won, `'b'` if the Blue player has won, `'tie'` if the result of the game is a tie, or the empty string `''` if the game is not over yet.

## AIAction Format
