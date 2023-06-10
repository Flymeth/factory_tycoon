from typing import Any
from pygame import display, Rect, Surface, transform, K_ESCAPE, MOUSEBUTTONDOWN, mouse, key
from gui.selector import Selector
from gui._assets import Button
from textures import get_texture
from fonts import TEXT_FONT

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