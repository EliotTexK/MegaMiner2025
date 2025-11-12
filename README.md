# MegaMiner 2025

MegaMiner is a yearly competition held by Computer Science students at Missouri S&T. Teams of up to 4 people create AI agents to compete in a video game tournament. This year, the game is ApocaWarlords. For details on how to play, go to the rules folder in this repository, and read the README.md file there.

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
Go to the Visualizer folder/directory where you put the executable. Then, double-click it, or run it using the command-line. Click Play Game

## How To Run The Backend ( No Visualizer )
Change directories to the backendRun it with the following command:
`python3 main.py`
