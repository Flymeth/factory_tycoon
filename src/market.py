from items import Item
from custom_events_identifier import PROCESS_EVENT
from blocks import *

class Market:
    def __init__(self, game) -> None:
        from _main import Game

        self.game: Game= game
        self.courts: dict[type[Item], float] = {} # {item_type: court_value}
        self.shop: dict[type[Block], float] = {
            GlobalSeller: 50000,
            Convoyer: 500,
            DiamondGenerator: 75000,
            Connecter: 25000,
            Sorter: 25000
        }

        # self.game.add_event(PROCESS_EVENT, lambda g,e: self.decrease_values())
        self.game.each(10000, (lambda g, e: self.decrease_values()))
        pass
    def get_court(self, item: Item):
        if not item.__class__ in self.courts:
            self.courts[item.__class__]= 1
        return self.courts[item.__class__]
    def selled(self, item: Item):
        self.courts[item.__class__]+= 1 /1000 # Redos this shity formula
    def decrease_values(self):
        for item in self.courts:
            self.courts[item]-= 1 /1000
        
        if self.game.DEV_MODE:
            print(f"Items value has been decreased.")