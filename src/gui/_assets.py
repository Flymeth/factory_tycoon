from pygame import Rect, Surface, mouse, MOUSEBUTTONDOWN, transform
from textures import no_texture, get_texture
from typing import Literal, Callable
from fonts import TITLE_FONT

class GUI():
    def __init__(self, game, rect: Rect, background: Surface, parent: Surface | None = None) -> None:
        from _main import Game

        self.game: Game = game
        self.rect= rect
        self.background= background
        self.parent= parent or self.game.pygame.screen
        self.active: bool= True

        self.game.add_event(MOUSEBUTTONDOWN, lambda g, e: self.__handle_click__())
    @property
    def _global_rect(self) -> Rect:
        parent_rect= self.parent.get_rect()
        return Rect(
            parent_rect.left + self.rect.left, parent_rect.top + self.rect.top,
            *self.rect.size
        )
    def __handle_click__(self):
        if not (self.active and mouse.get_pressed()[0]): return
        mx, my = mouse.get_pos()
        rect= self._global_rect
        if (
            rect.left <= mx <= rect.right
            and rect.top <= my <= rect.bottom
        ):
            return self.on_click()

    def get_texture(self) -> Surface: return no_texture()
    def on_click(self) -> None: pass
    def set_freezing(self, freeze: bool, do_for_player_interaction: bool= False) -> None:
        self.game.freeze_process = self.game.cam.freeze_position = self.game.cam.freeze_zoom = freeze
        if do_for_player_interaction:
            self.game.player.freeze_blocks_interaction= freeze
    def draw(self):
        self.parent.blit(self.get_texture(), self.rect.topleft)
    def process(self):
        self.active= True
        while self.active and not self.game.update():
            self.update()
        pass
class Button():
    def __init__(self, game, rect: Rect, text: str, btn_type: Literal["yes", "no"] | None = None, on_click: Callable[[], None] = lambda:0) -> None:
        """ If the draw_on surface is none, it will take the screen as the surface
        """
        
        from _main import Game
        self.game: Game = game
        self.rect= rect
        self.onclick = on_click
        self.change_type(btn_type)

        self.caption= text
        self.active= False

        self.click_event_id = self.game.add_event(MOUSEBUTTONDOWN, lambda g,e: self.__clicked__())
    def change_type(self, btn_type: Literal["yes", "no"] | None = None):
        texture= get_texture("uis", f"button{f'_{btn_type}' if btn_type else ''}")
        self.texture= transform.scale(texture, self.rect.size)
    def draw(self):
        texture= self.texture
        font_size = self.rect.width / len(self.caption)
        font, font_rect = TITLE_FONT.render(self.caption, size= font_size)
        texture.blit(font, 
            ((self.rect.width - font_rect.width)/2, (self.rect.height - font_rect.height)/2)
        )

        self.game.draw(texture, self.rect.topleft)
    def __clicked__(self):
        if not (self.active and mouse.get_pressed()[0]): return
        #                                          ^^^ = left click
        mx, my = mouse.get_pos()
        if (
            self.rect.left <= mx <= self.rect.right
            and self.rect.top <= my <= self.rect.bottom
        ):
            return self.onclick()
