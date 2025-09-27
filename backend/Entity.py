import Constants

class Entity:
    def __int__(self, health: int, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.health = health