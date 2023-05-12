from quests import Quest
from blocks import Block
from items import Item

class Player:
    def __init__(self, name: str, default_credits= 0, default_quests: list[Quest]= []) -> None:
        self.name= name
        self.credits= default_credits
        self.active_quests= default_quests
        self.achieved_quests: list[Quest]= []
        self.inventory: list[Block] = []
        pass
    def sell(self, item: Item):
        pass