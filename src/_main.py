import blocks
import items
import map
import player
import quests
import market
from direction_sys import Direction
from uuid import uuid1, UUID
from typing import Callable, Self
import pygame as pg

class Modules:
    blocks= blocks
    items= items
    map= map
    player= player
    quests= quests
    market= market

class Pygame():
    def __init__(self, fps: int) -> None:
        pg.init()
        self.fps= fps

        self.screen = pg.display.set_mode(size= (750, 200))
        pg.display.flip()
        self.clock = pg.time.Clock()
        self.app = pg
        self.dt = 0
    def tick(self) -> float:
        self.dt = self.clock.tick(self.fps)/ 1000
        return self.dt

class Game:
    Modules= Modules
    def __init__(self, player_name: str, max_fps= 60) -> None:
        self.map= map.Map(self, init= [[blocks.GlobalSeller(self)]])
        self.player= player.Player(self, player_name)
        self.marked= market.Market(self)
        self.quests= [Q(self) for Q in quests if type(Q) == quests.Quest and Q.__class__ != quests.Quest]

        self.pygame= Pygame(max_fps)
        self.events: dict[str, list[tuple[UUID, Callable[[Self, pg.event.Event], None]]]]= {}
        pass
    def start(self):
        """ Starts the game
        """
        while 1:
            for event in self.pygame.app.event.get():
                self.call_event(event.type, event)

            self.pygame.screen.fill("orange")
            self.pygame.tick()
    def quit(self):
        """ Quits and close the game
        """
        return self.pygame.app.quit
    
    # EVENT MANAGERS ---
    def add_event(self, ev_name: str, handler: Callable[[Self, pg.event.Event], None]):
        """ Add an handler to an event
            Returns the handler's id
        """
        ev_id= uuid1()
        if not ev_name in self.events:
            self.events[ev_name]= []
        self.events[ev_name].append((ev_id, handler))
        return ev_id
    def rmv_event(self, ev_name: str):
        """ Remove all handlers from an event
        """
        if ev_name in self.events:
            del self.events[ev_name]
    def rmv_handler(self, predicate: UUID | Callable[[Self, pg.event.Event], None]) -> bool:
        """ Remove an event's handler
        """
        for name in self.events:
            for ev_data in self.events[name]:
                if predicate in ev_data:
                    self.events[name].remove(ev_data)
                    if not len(self.events[name]):
                        self.rmv_event(name)
                    return ev_data
        raise IndexError("Event not in the event list")
    def fire_event(self, ev_name: str, ev_data: pg.event.Event):
        """ Fires an event and call all its handlers
        """
        if not ev_name in self.events: return []
        return [handler(self, ev_data) for _, handler in self.events[ev_name]]
    # ---

if __name__ == "__main__":
    print(Game.Modules.blocks)
    g = Game("Cobaille")
    g.map.generate_chunks(Direction.fast("wn"), 10)
    print(g.map.matrice[9][9].position)
    print(g.map)
    print(g.map.center)

    e= g.add_event("test", lambda g, e: print(f"hello {g.player.name}, you fired the event no. {e.type}!"))
    g.add_event("test", lambda g, e: print(f"hello {g.player.name}, you fired the event no. {e.type}!"))
    g.add_event("test", lambda g, e: print(f"hello {g.player.name}, you fired the event no. {e.type}!"))
    g.add_event("test", lambda g, e: print(f"hello {g.player.name}, you fired the event no. {e.type}!"))
    print(g.events)
    g.fire_event("test", pg.event.Event(156))
    g.rmv_handler(e)
    print(g.events)
    g.rmv_event("test")
    print(g.events)

    print(g.quests)