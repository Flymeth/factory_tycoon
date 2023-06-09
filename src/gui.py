from pygame import Surface, display, transform, MOUSEBUTTONDOWN, mouse, MOUSEWHEEL, key, K_ESCAPE, Rect
from typing import Any, Literal, Callable
from textures import get_texture
from fonts import TEXT_FONT, TITLE_FONT

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

        self.click_event_id = self.game.add_event(MOUSEBUTTONDOWN, lambda g,e: self.clicked())
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
    def clicked(self):
        if not (self.active and mouse.get_pressed()[0]): return
        #                                          ^^^ = left click
        mx, my = mouse.get_pos()
        if (
            self.rect.left <= mx <= self.rect.right
            and self.rect.top <= my <= self.rect.bottom
        ):
            return self.onclick()

class InventoryBar():
    def __init__(self, game, content: list[tuple[Any, int]] = []) -> None:
        from _main import Game
        from blocks import Block

        self.game: Game= game
        self.content: list[tuple[Block, int]] = content
        self.selected: int = -1
        self.items_size= 50
        self.paddings= 5
        pass
    def get_selected_block(self):
        """ Returns the block's instance of the selected block and generate another to replace it
        """
        assert self.selected >= 0, "Player has not selected any block"
    
        selected, amount = self.content[self.selected]
        if not amount: return None
        self.content[self.selected]= (selected.__class__(self.game), amount)
        return selected
    def modify_amount(self, block: Any, add: int):
        for index, (nav_block, amount) in enumerate(self.content):
            if type(nav_block) == type(block):
                self.content[index]= (nav_block, max(0, amount + add))
                return
        # If python reach this point, that means that the item is not in the inventory, so we add it
        self.content.append((block, max(0, add)))
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
        
        for index, (block, amount) in enumerate(self.content):
            x, y = (
                self.paddings + index * (self.items_size + self.paddings),
                self.paddings
            )
            texture= transform.scale(
                block.texture,
                [self.items_size] * 2
            )
            
            if index != self.selected: texture.set_alpha(120)
            if not amount: texture.set_alpha(50)
            
            amount_text, amount_rect = TEXT_FONT.render(str(amount), fgcolor= (255, 255, 255), size= 15)
            texture.blit(amount_text, (self.items_size - amount_rect.width - 2, self.items_size - amount_rect.height - 2))

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
        gui = transform.scale(get_texture("uis", "selector_bg"), (w, h))
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

        self.game.draw(gui, (x, y))
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

class MarketGUI():
    def __init__(self, game, sellable: dict[Any, float], freeze_game: bool = True) -> None:
        from blocks import Block
        from _main import Game

        self.game: Game = game
        self.content: dict[Block, float] = sellable

        self.freezing= freeze_game
        self.setfreeze(freeze_game)
        self.active= False
        self.active_item: Block | None= None
        self.current_selector: Selector | None= None

        # GUI Rect Set
        win_size= display.get_window_size()
        w, h = (
            win_size[0]/ 3.5,
            win_size[1]/ 1.2
        )
        x, y = [
            (win_size[i] - (w, h)[i])/2
            for i in range(2)
        ]
        self.texture= transform.scale(get_texture("uis", "market"), (w, h))
        
        self.gui_rect= Rect(x, y, w, h)
        self.item_selector_rect = Rect(
            12*w /32, 16*h /64,
            9*w /32,  9*h /64
        )

        button_w, button_h = w * .5, 50
        self.confirm_button = Button(self.game, Rect(
            x + (w - button_w)/2, y + self.gui_rect.height - 2* button_h,
            button_w, button_h
        ), "BUY", "no", lambda: self.buy())

        self.game.add_event(MOUSEBUTTONDOWN, lambda g,e: self.clicked())
    def buy(self):
        if not (self.active and self.active_item): return
        item_price = self.content[self.active_item]
        if item_price > self.game.player.balance: return
        if self.game.DEV_MODE:
            print(f"Player has bought {self.active_item.identifier} at ${item_price}.")

        self.game.player.gain(-item_price)
        self.game.player.inventory_bar.modify_amount(self.active_item, 1)
        self.game.marked.bought.append((type(self.active_item), item_price))
        return self.end()
    def update(self):
        if key.get_pressed()[K_ESCAPE] and not self.current_selector:
            return self.end()

        gui = self.texture.copy()
        if self.active_item:
            mask= Surface(self.item_selector_rect.size)
            mask.fill((0, 0, 0))

            item_texture = transform.scale(self.active_item.texture, self.item_selector_rect.size)

            item_price = self.content[self.active_item]

            price_surface, price_rect= TEXT_FONT.render(f"${round(item_price, 2)}", size= 15)
            price_box_rect = Rect(
                (self.gui_rect.width - price_rect.width)/2, self.item_selector_rect.bottom + price_rect.height,
                *price_rect.size
            )
            
            gui.blits((
                (mask, self.item_selector_rect.topleft),
                (item_texture, self.item_selector_rect.topleft),
                (price_surface, price_box_rect.topleft)
            ))
        else:
            self.confirm_button.active= False
        self.game.draw(gui, self.gui_rect.topleft)
        if self.active_item:
            self.confirm_button.change_type("yes" if item_price <= self.game.player.balance else "no")
            self.confirm_button.draw()
    def clicked(self):
        if not (self.active and mouse.get_pressed()[0]) or self.current_selector: return
        #                                          ^^^ = left click 
        
        mx, my = mouse.get_pos()
        translate_x, translate_y = self.gui_rect.topleft
        if(
            translate_x + self.item_selector_rect.left <= mx <= translate_x + self.item_selector_rect.right
            and translate_y + self.item_selector_rect.top <= my <= translate_y + self.item_selector_rect.bottom
        ):
            self.confirm_button.active= False
            self.current_selector = Selector(self.game, list(self.content.keys()))
            selected = self.current_selector.get()
            self.setfreeze(self.freezing)
            self.current_selector = None
            if not selected: return
            self.active_item= selected
            self.confirm_button.active= True
    def process(self):
        self.active= True
        while self.active and not self.game.update():
            self.update()
        return self.end()
    def end(self):
        self.active= False
        self.setfreeze(False)
    def setfreeze(self, freezing= False):
        self.game.freeze_process = self.game.cam.freeze_position = self.game.cam.freeze_zoom = self.game.player.freeze_blocks_interaction = freezing

    
