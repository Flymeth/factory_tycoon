from pygame import Surface, display, transform, MOUSEBUTTONDOWN, mouse, MOUSEWHEEL, key, K_ESCAPE, Rect
from typing import Any
from textures import get_texture

class InventoryBar():
    def __init__(self, game, content: list[Any] = []) -> None:
        from _main import Game
        from blocks import Block

        self.game: Game= game
        self.content: list[Block]= content
        self.selected: int = -1
        self.items_size= 50
        self.paddings= 5
        pass
    def get_selected_block(self):
        """ Returns the block's instance of the selected block and generate another to replace it
        """
        assert self.selected >= 0, "Player has not selected any block"

        selected = self.content[self.selected]
        self.content[self.selected]= self.content[self.selected].__class__(self.game)
        return selected
    def get_rect(self):
        """ Returns the rect of the gui
        """
        window_size = display.get_window_size()
        width, height = (
            self.paddings + len(self.content) * (self.items_size + self.paddings),
            self.paddings *2 + self.items_size
        )
        return Rect((window_size[0] - width)/2, window_size[1] - (height + self.paddings), width, height)
    def draw(self):
        assert self.game, "Cannot draw without the game object"

        rect = self.get_rect()
        gui= Surface(rect.size)
        
        for index, block in enumerate(self.content):
            x, y = (
                self.paddings + index * (self.items_size + self.paddings),
                self.paddings
            )
            texture= transform.scale(
                block.texture,
                [self.items_size] * 2
            )
            if index != self.selected: texture.set_alpha(120)
            
            gui.blit(texture, (x, y))

        self.game.draw(gui, rect.topleft)

class Selector():
    def __init__(self, game, choices: list[Any], items_per_row= 3, freeze_game= False, scroll_speed = 5) -> None:
        assert choices, "Invalid choices provided (it must be a list with at least 1 element"

        from _main import Game
        from items import Item
        from blocks import Block

        self.game: Game= game
        self.choices: list[Item | Block]= choices
        self.choosed: Block | Item | None= None
        self.scrollDown= 0
        self.items_per_row= items_per_row
        self.items_margin= 5
        self.box_padding = 10
        self.scroll_speed = scroll_speed

        self.game.player.freeze_blocks_interaction = True
        self.game.freeze_process = self.game.cam.freeze_position = self.game.cam.freeze_zoom = freeze_game
        self.active= False

        self.game.add_event(MOUSEBUTTONDOWN, lambda g, e: self.clicked())
        self.game.add_event(MOUSEWHEEL, lambda g, e: self.scrolling(e.y))
        self.rects: list[tuple[tuple[float], tuple[float], Block | Item]]= [] # (coordonates_tl, coordonates_br, item)
        self.gui_rect: tuple[tuple[float], tuple[float]]= ((0, 0), (0, 0)) # (coordonates_tl, coordonates_br)
        self.can_scroll_down= False
        self.can_scroll_up= False
        pass
    def update(self):
        if key.get_pressed()[K_ESCAPE]:
            return self.end()

        win_size= display.get_window_size()
        w, h = (
            win_size[0]/ 3.5,
            win_size[1]/ 1.2
        )
        x, y = [
            (win_size[i] - (w, h)[i])/2
            for i in range(2)
        ]
        gui= Surface((w, h))
        bg= get_texture("uis", "selector_bg")
        gui.blit(transform.scale(bg, (w, h)), (0, 0))

        items_size= (w - 2*self.box_padding) / self.items_per_row - self.items_margin /2

        self.gui_rect= (
            (x + self.box_padding/2, x + w - self.box_padding/2),
            (y + self.box_padding/2, y + h - self.box_padding/2)
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
                -items_size <= item_y <= h
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

        self.game.pygame.screen.blit(gui, (x, y))
    def clicked(self):
        if not (self.active and mouse.get_pressed()[0]): return
        #                                          ^^^ = left click 
        mouse_position = mouse.get_pos()
        for tl, br, item in self.rects:
            if (
                tl[0] <= mouse_position[0] <= br[0]
                and tl[1] <= mouse_position[1] <= br[1]
            ):
                self.choosed= item
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
        self.active= True
        while not (self.choosed or self.game.update()) and self.active:
            self.update()
        return self.end()
    def end(self):
        self.active= False
        self.unfreeze()
        return self.choosed
    def unfreeze(self):
        self.game.freeze_process = self.game.cam.freeze_position = self.game.cam.freeze_zoom = self.game.player.freeze_blocks_interaction = False