from quests import Quest
from blocks import Block
from items import Item

class Player:
    def __init__(self, game, name: str, default_credits= 0, default_quests: list[Quest]= []) -> None:
        from _main import Game

        self.game: Game= game
        self.name= name
        self.credits= default_credits
        self.active_quests= default_quests
        self.achieved_quests: list[Quest]= []
        self.inventory: list[Block] = []
        pass
    def gain(self, amount: float) -> float:
        self.credits+= amount
        return self.credits