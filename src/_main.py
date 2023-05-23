import blocks
import items
import map
import player
import quests
import market
from direction_sys import Direction
from uuid import uuid1, UUID
from typing import Callable, Any, Self
import pygame as pg
from camera import Camera
from textures import create_surface

DEV_MODE= True

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
        window_size= pg.display.get_desktop_sizes()[0]
        self.screen = pg.display.set_mode(
            size= [(size /2 if DEV_MODE else size) for size in window_size], 
            flags= pg.DOUBLEBUF | (
                0 if DEV_MODE 
                else pg.FULLSCREEN | pg.SCALED | pg.NOFRAME
            ),
            vsync= True
        )
        self.screen.set_alpha(None)
        pg.display.flip()
        pg.display.set_caption(f"Factory Tycoon ({'DEVELOPMENT MODE' if DEV_MODE else 'RELEASE MODE'})")
        pg.display.set_icon(create_surface("src/assets/icon.png"))
        self.clock = pg.time.Clock()
        self.app = pg
        self.dt = 0
    def next_tick(self) -> float:
        self.dt = self.clock.tick(self.fps)/ 1000
        return self.dt

class Game:
    Modules= Modules
    def __init__(self, player_name: str, max_fps= 144) -> None:
        self.pygame= Pygame(max_fps)
        self.events: dict[str, list[tuple[UUID, Callable[[Self, pg.event.Event], None], bool]]]= {}
        self.running= True
        self.DEV_MODE= DEV_MODE
        self.quests: list[quests.Quest]= []
        for key in dir(quests):
            Q= getattr(quests, key)
            if type(Q) == type(quests.Quest) and Q != quests.Quest:
                self.quests.insert(0, Q(self))
        self.cam= Camera(self)

        init_block = blocks.Trash(self)
        init_block.block_bellow = init_block
        self.map= map.Map(self, init_block= init_block)
        self.player= player.Player(self, player_name)
        self.marked= market.Market(self)
        self.require_drawing= []
        pass
    def start(self):
        """ Starts the game
        """
        self.add_event(pg.QUIT, lambda g, e: self.quit())
        while 1:
            self.cam.draw()
            pg.display.update()

            for event in self.pygame.app.event.get():
                self.fire_event(event.type, event)
            self.fire_event("tick", pg.event.Event(-1, {"dt": self.pygame.dt}))
            if not self.running: break

            self.pygame.next_tick()
    def quit(self):
        """ Quits and close the game
        """
        self.running= False
        self.pygame.app.quit()
        return exit(0)
    
    # EVENT MANAGERS
    def add_event(self, ev_identifier: Any, handler: Callable[[Self, pg.event.Event], None], once= False):
        """ Add an handler to an event
            Returns the handler's id
        """
        ev_id= uuid1()
        if not ev_identifier in self.events:
            self.events[ev_identifier]= []
        self.events[ev_identifier].append((ev_id, handler, once))
        return ev_id
    def rmv_event(self, ev_name: str):
        """ Remove all handlers from an event
        """
        if ev_name in self.events:
            del self.events[ev_name]
    def rmv_handler(self, predicate: UUID | Callable[[Self, pg.event.Event], None]):
        """ Remove an event's handler
        """
        for name in self.events:
            for ev_data in self.events[name]:
                if predicate in ev_data:
                    self.events[name].remove(ev_data)
                    if not len(self.events[name]):
                        self.rmv_event(name)
                    return
        raise IndexError("Event not in the event list")
    def fire_event(self, ev_identifier: Any, ev_data: pg.event.Event):
        """ Fires an event and call all its handlers
        """
        if not ev_identifier in self.events: return
        for uuid, handler, once in self.events[ev_identifier]:
            handler(self, ev_data)
            if once: self.rmv_handler(uuid)
if __name__ == "__main__":
    print(Game.Modules.blocks)
    g = Game("Cobaille")

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

    g.map.generate_chunks(Direction.fast("a"), 5)

    my_seller= blocks.GlobalSeller(g)
    g.map.place(my_seller, (1, 1))

    no_textured_block = blocks.Sorter(g)
    g.map.place(no_textured_block, (5, 5))
    
    print("MAP BEFORE START:\n", str(g.map))
    print(g.map.get_block(0, 0))
    g.start()
