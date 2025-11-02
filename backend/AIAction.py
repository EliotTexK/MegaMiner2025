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
