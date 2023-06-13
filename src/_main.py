import blocks
import items
import map
import player
import quests
import market
import gui
import utils
import menu
from utils import properties
from direction_sys import Direction
from typing import Callable, Any, Self
import pygame as pg
from camera import Camera
from textures import create_surface
from custom_events_identifier import *

DEV_MODE: bool= properties.game_properties.get("DEV_MODE")

class TimeInformation():
    MS_TIMER_INTERVAL= 1
    def __init__(self, time: int, possible_difference: int):
        self.time= {
            "ms": time,
            "s": time / 1000,
            "m": time / (1000 * 60),
            "h": time / (1000 * 60**2),
            "d": time / (1000 * 60**2 * 24)
        }
        """
            ```py
                {
                    "ms":  int, # Time in miliseconds
                    "s": float, # Time in seconds
                    "m": float, # Time in minutes
                    "h": float, # Time in hours
                    "d": float, # Time in days
                }
            ```
        """
        self.approximated_at= possible_difference
    def __str__(self) -> str:
        approximation= int(self.approximated_at/2)
        return f"TIME<{round(self.time['s'] + approximation/1000, 3)}s (+/- {approximation}ms)>"

class Modules:
    blocks= blocks
    items= items
    map= map
    player= player
    quests= quests
    market= market
    gui= gui
    utils= utils
    menu= menu

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
        pg.display.flip()
        pg.display.set_caption(f"Factory Tycoon ({'DEVELOPMENT MODE' if DEV_MODE else 'RELEASE MODE'})")
        pg.display.set_icon(create_surface("src/assets/icon.png"))
        self.clock = pg.time.Clock()
        self.app = pg
        self.dt = 0
        self.ticks= 0
        self.ms= 0
    def next_tick(self) -> float:
        self.dt = self.clock.tick(self.fps)
        self.ticks+= 1
        return self.dt

class Game:
    Modules= Modules
    def __init__(self, player_name: str, max_fps= 144) -> None:
        self.pygame= Pygame(max_fps)
        self.next_event_id= 0
        self.events: dict[str, list[tuple[int, Callable[[Self, pg.event.Event], None], bool]]]= {}
        self.running= True
        self.properties= properties.game_properties
        self.DEV_MODE= DEV_MODE
        self.AllTheQuests: list[type[quests.Quest]]= quests.AllTheQuests
        self.freeze_process= False
        self.require_drawing= []
        self.cache: dict[str, any]= {}
        self.intervals: dict[int, list[Callable[[Self, pg.event.Event], None]]] = {}
        self.__mouse_clicking_position: list[int]= []
        self.scene= "menu"

        # Shorthands
        self.screen= self.pygame.screen
        self.draw= self.screen.blit

        # Init all modules
        self.cam= Camera(self)
        self.map= map.Map(self)
        self.player= player.Player(self, player_name, quests_to_achieve= self.AllTheQuests.copy(), default_balance= 0)
        self.marked= market.Market(self)
        self.menu = menu.Menu(self)

        # Setting up events
        self.add_event(PROCESS_EVENT, lambda g, e: self.__update_interval_functions__())
        self.add_event(pg.MOUSEBUTTONDOWN, lambda g, e: self.__mouse_clicking__(e.button, True))
        self.add_event(pg.MOUSEBUTTONUP, lambda g, e: self.__mouse_clicking__(e.button, False))
    def __mouse_clicking__(self, button: int, active: bool):
        if button in self.__mouse_clicking_position:
            if not active:
                self.__mouse_clicking_position.remove(button)
                event = (
                    LEFT_CLICK if button == 1 else
                    MIDDLE_CLICK if button == 2 else RIGHT_CLICK
                )
                self.fire_event(event, pg.event.Event(event))
        elif active:
            self.__mouse_clicking_position.append(button)
    @property
    def time_infos(self) -> TimeInformation:
        """ Get time informations since the app started
        """
        time= self.pygame.ms
        possible_difference= time - self.cache.get("last_tick", 0)
        self.cache["last_tick"]= time
        return TimeInformation(time, possible_difference)
    def start(self):
        """ Starts the game
        """
        self.add_event(pg.QUIT, lambda g, e: self.quit())
        pg.time.set_timer(PROCESS_EVENT, TimeInformation.MS_TIMER_INTERVAL)
        while not self.update(): pass

    def update(self) -> bool:
        """ Make a game update
            Returns if the program should stop
        """
        pg.display.update()

        for event in self.pygame.app.event.get():
            self.fire_event(event.type, event)
            if event.type == PROCESS_EVENT:
                self.pygame.ms+= TimeInformation.MS_TIMER_INTERVAL
        self.fire_event(DRAW_EVENT, pg.event.Event(DRAW_EVENT, {"dt": self.pygame.dt, "index": self.pygame.ticks}))
        if not self.running: return True

        self.pygame.next_tick()
        return False
    def quit(self):
        """ Quits and close the game
        """
        self.running= False
        self.pygame.app.quit()
        return exit(0)
    
    def change_scene(self, new_scene: str):
        self.scene= new_scene
    
    # EVENT MANAGERS
    def each(self, ms: int, *handlers: Callable[[Self, pg.event.Event], None], only_for_scenes: list[str]= []):
        """ Execute an handler each x miliseconds

            Argument <only_for_scenes>:
                See the <fire_event> function
        """
        if not ms in self.intervals:
            self.intervals[ms]= []
        if only_for_scenes:
            handlers= [
                lambda g, e: (
                    handler(g, e)
                ) if self.scene in only_for_scenes else 0
                for handler in handlers
            ]
        self.intervals[ms]+= list(handlers)
    def __update_interval_functions__(self):
        infos = self.time_infos
        for ms, handlers in self.intervals.items():
            if infos.time["ms"] % ms <= infos.approximated_at:
                [f(self, pg.event.Event(PROCESS_EVENT, {"time": infos})) for f in handlers]
    def add_event(self, ev_identifier: Any, handler: Callable[[Self, pg.event.Event], None], once= False, only_for_scenes: list[str]= []):
        """ Add an handler to an event
            Returns the handler's id

            Argument <only_for_scenes>:
                If this event should be fired only for certain scene. Keep this list empty to update it for any scenes
        """
        ev_id= self.next_event_id
        if not ev_identifier in self.events:
            self.events[ev_identifier]= []
        fn = handler
        if only_for_scenes:
            fn= lambda g, e: (handler(g, e) if self.scene in only_for_scenes else 0)
        self.events[ev_identifier].append((ev_id, fn, once))

        self.next_event_id+= 1
        return ev_id
    def rmv_event(self, ev_name: str):
        """ Remove all handlers from an event
        """
        if ev_name in self.events:
            del self.events[ev_name]
    def rmv_handler(self, predicate: int | Callable[[Self, pg.event.Event], None]):
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
    def get_event_data(self, predicate: int | Callable[[Self, pg.event.Event], None]):
        for name in self.events:
            for ev_data in self.events[name]:
                if predicate in ev_data:
                    return ev_data
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
    print(g.player.quests)

    g.map.generate_chunks(Direction.fast("a"), 5)

    # my_seller= blocks.GlobalSeller(g)
    # g.map.place(my_seller, (1, 1))

    # no_textured_block = blocks.Sorter(g)
    # g.map.place(no_textured_block, (5, 5))
    
    print("MAP BEFORE START:\n", str(g.map))
    print(g.map.get_block(0, 0))
    g.start()
