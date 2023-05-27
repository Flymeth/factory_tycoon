from items import Item
from custom_events_identifier import PROCESS_EVENT

class Market:
    def __init__(self, game) -> None:
        from _main import Game

        self.game: Game= game
        self.courts: dict[type[Item], float] = {} # {item_type: court_value}
        self.shop = {}

        self.game.add_event(PROCESS_EVENT, lambda g,e: self.increase_values())
        pass
    def get_court(self, item: Item):
        if not item in self.courts:
            self.courts[item.__class__]= 1
        return self.courts[item.__class__]
    def selled(self, item: Item):
        self.courts[item.__class__]-= 1 /1000 # Redos this shity formula
    def increase_values(self):
        now= self.game.time_infos
        if now.time["ms"] % 1000 <= now.approximated_at:
            for item in self.courts:
                self.courts[item]+= 1 /1000
            
            if self.game.DEV_MODE:
                print(f"Items value has been increased.")