import blocks
import items
import map
import player
import quests

class Modules:
    blocks= blocks
    items= items
    map= map
    player= player
    quests= quests

class Game:
    Modules= Modules
    def __init__(self) -> None:
        pass

if __name__ == "__main__":
    print(Game.Modules.blocks)