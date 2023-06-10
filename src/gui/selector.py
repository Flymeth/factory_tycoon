from pygame import display, transform, MOUSEBUTTONDOWN, mouse, MOUSEWHEEL, key, K_ESCAPE, Rect
from typing import Any
from textures import get_texture
from gui._assets import Page

class Selector(Page):
    def __init__(self, game, choices: list[Any], items_per_row= 3, freeze_game= False, scroll_speed = 5) -> None:
        assert choices, "Invalid choices provided (it must be a list with at least 1 element"
        from items import Item
        from blocks import Block


        self.choices: list[Item | Block]= choices
        self.choosed: Block | Item | None= None
        self.scrollDown= 0
        self.items_per_row= items_per_row
        self.items_margin= 5
        self.box_padding = 10
        self.scroll_speed = scroll_speed

        win_size= display.get_window_size()
        w, h = (
            win_size[0]/ 3.5,
            win_size[1]/ 1.2
        )
        x, y = [
            (win_size[i] - (w, h)[i])/2
            for i in range(2)
        ]
        gui = transform.scale(get_texture("uis", "selector_bg"), (w, h))
        super().__init__(game, Rect(x, y, w, h), gui)

        self.set_freezing(True, True)

        self.rects: list[tuple[tuple[float], tuple[float], Block | Item]]= [] # (coordonates_tl, coordonates_br, item)
        self.gui_rect: tuple[tuple[float], tuple[float]]= ((0, 0), (0, 0)) # (coordonates_tl, coordonates_br)
        self.can_scroll_down= False
        self.can_scroll_up= False
        pass
    def get_texture(self):
        gui = self.background.copy()
        items_size= (self.rect.width - 2*self.box_padding) / self.items_per_row - self.items_margin /2

        self.gui_rect= (
            (self.rect.left + self.box_padding/2, self.rect.right - self.box_padding/2),
            (self.rect.top + self.box_padding/2, self.rect.bottom - self.box_padding/2)
        )

        self.rects= []
        self.can_scroll_up = self.can_scroll_down = False
        for index, item in enumerate(self.choices):
            translates_time= index %self.items_per_row, index //self.items_per_row
            item_x, item_y= [
                translates_time[i] * (items_size + self.items_margin/2) + self.box_padding
                for i in range(2)
            ]
            item_y+= self.scrollDown
            if not (
                -items_size <= item_y <= self.rect.height
            ): 
                if not index:
                    self.can_scroll_up= True
                elif index == len(self.choices) -1:
                    self.can_scroll_down= True

            item_choice_texture= transform.scale(get_texture("uis", "selector_item"), [items_size] *2)
            item_texture= transform.scale(item.texture, [items_size/ 2] *2)
            
            item_choice_texture.blit(item_texture, [(items_size - items_size/2) /2] *2)
            gui.blit(item_choice_texture, (item_x, item_y))

            global_position = (self.gui_rect[0][0] + item_x, self.gui_rect[1][0] + item_y)
            self.rects.append((
                global_position,
                (global_position[0] + items_size, global_position[1] + items_size),
                item
            ))

        return gui
    def on_click(self):
        mouse_position = mouse.get_pos()
        for tl, br, item in self.rects:
            if (
                tl[0] <= mouse_position[0] <= br[0]
                and tl[1] <= mouse_position[1] <= br[1]
            ):
                self.choosed= item
                self.active= False
                break
    def scrolling(self, scroll_y: int):
        if not self.active: return
        if scroll_y < 0 and not self.can_scroll_up:
            self.scrollDown = 0
            return
        elif scroll_y > 0 and not self.can_scroll_down:
            return
        self.scrollDown+= scroll_y * self.scroll_speed
    def get(self) -> Any | None:
        self.process()
        return self.choosed
    def on_end(self):
        self.set_freezing(False, True)
        return self.choosed
