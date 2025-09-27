import sys
import subprocess
import Game

file_path : str = "C:/Users/kenji/OneDrive/Desktop/GitHub Projects/Mega-Miner-2025-Visualizer/MegaMiner_BackEnd/AI_Agents/Agent1.py"

#game = Game.Game()


if __name__ == "__main__":

    print(f"Arguments count: {len(sys.argv)}")
    if len(sys.argv) > 1:
        print(sys.argv[1])
        try:                 
            ans = subprocess.check_output(["python", sys.argv[1]])
            print(ans)
        except subprocess.CalledProcessError as e:
           print(f"Command failed with return code {e.returncode}")
    try:
        ans = subprocess.check_output(["python", file_path])
        print(ans)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
    
    if can_start:
        game.run()

    