from gui._assets import Button
from textures import VideoSurface
from pygame import Rect, display, BLEND_RGB_ADD
from custom_events_identifier import DRAW_EVENT
from fonts import TITLE_FONT_BOLD
from colors import orange

class Menu():
    def __init__(self, game) -> None:
        from _main import Game
        self.game: Game= game
        self.rect= Rect(0, 0, *display.get_window_size())
        self.video= VideoSurface("misc", "menu_bg", ext= "mp4", size= self.rect.size)
        self.game.add_event(DRAW_EVENT, lambda g, e: self.draw(), only_for_scenes= ["menu"])

        # Setting up all buttons
        screen_rect = self.game.screen.get_rect()

        launch_button_size = (100, 50)
        self.launch_button = Button(game, Rect(
            screen_rect.centerx - launch_button_size[0]/2,
            screen_rect.centery - launch_button_size[1]/2,
            *launch_button_size
        ), "START", on_click= lambda: self.game.change_scene("ingame"))
    def draw(self):
        screen_rect = self.game.screen.get_rect()

        # background
        self.video.update(.5)
        self.game.draw(self.video, (0, 0))

        # title
        title, title_rect = TITLE_FONT_BOLD.render("Factory Tycoon", size= 35, fgcolor= orange)
        self.game.draw(title, (
            (screen_rect.width - title_rect.width)/2,
            (title_rect.height)
        ), special_flags= BLEND_RGB_ADD)

        # launch button
        self.launch_button.draw()