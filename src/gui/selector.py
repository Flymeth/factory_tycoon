from pygame import display, transform, mouse, Rect, MOUSEWHEEL
from typing import Any
from textures import get_texture
from gui._assets import Page

class Selector(Page):
    def __init__(self, game, choices: list[Any], items_per_row= 3, freeze_game= True, scroll_speed = 5) -> None:
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

        texture= get_texture("uis", "selector_bg")
        texture_rect= texture.get_rect()
        win_size= display.get_window_size()

        gui_height= win_size[1] - 50
        gui_width = texture_rect.width * gui_height/texture_rect.height
        x, y = [
            (win_size[i] - (gui_width, gui_height)[i])/2
            for i in range(2)
        ]
        super().__init__(game, Rect(x, y, gui_width, gui_height), texture)

        self.set_freezing(freeze_game, True)

        self.rects: list[tuple[Rect, Block | Item]]= []
        self.content_rect= Rect(x + self.box_padding, y + self.box_padding, gui_width - self.box_padding, gui_height - self.box_padding)
        self.can_scroll_down= False
        self.can_scroll_up= False

        self.game.add_event(MOUSEWHEEL, lambda g,e: self.scrolling(e.y))
        pass
    def get_texture(self):
        gui = self.background.copy()
        items_size= (self.rect.width - 2*self.box_padding) / self.items_per_row - self.items_margin /2

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
                -items_size <= item_y <= self.content_rect.height
            ): 
                if not index:
                    self.can_scroll_up= True
                elif index == len(self.choices) -1:
                    self.can_scroll_down= True

            item_choice_texture= transform.scale(get_texture("uis", "selector_item"), [items_size] *2)
            item_texture= transform.scale(item.texture, [items_size/ 2] *2)
            
            item_choice_texture.blit(item_texture, [(items_size - items_size/2) /2] *2)
            gui.blit(item_choice_texture, (item_x, item_y))

            global_rect = Rect(
                self.content_rect.left + item_x,
                self.content_rect.top + item_y,
                items_size,
                items_size
            )
            self.rects.append((global_rect, item))

        return gui
    def on_click(self):
        mouse_position = mouse.get_pos()
        for rect, item in self.rects:
            if (
                rect.left <= mouse_position[0] <= rect.right
                and rect.top <= mouse_position[1] <= rect.bottom
            ):
                self.choosed= item
                self.active= False
                break
    def scrolling(self, scroll_y: int):
        if not self.active: return
        if scroll_y < 0 and not self.can_scroll_down:
            self.scrollDown = 0
            return
        elif scroll_y > 0 and not self.can_scroll_up:
            return
        self.scrollDown+= scroll_y * self.scroll_speed
    def get(self) -> Any | None:
        self.process()
        return self.choosed
    def on_end(self):
        self.set_freezing(False, True)
        return self.choosed
