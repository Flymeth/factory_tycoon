from typing import Any
from pygame import display, Rect, Surface, transform, K_ESCAPE, MOUSEBUTTONDOWN, mouse, key
from gui.selector import Selector
from gui._assets import Button, Page
from textures import get_texture
from fonts import TEXT_FONT

class MarketGUI(Page):
    def __init__(self, game, sellable: dict[Any, float], freeze_game: bool = True) -> None:
        from blocks import Block

        self.content: dict[Block, float] = sellable
        self.active= False
        self.active_item: Block | None= None

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
        super().__init__(game, Rect(x, y, w, h), transform.scale(get_texture("uis", "market"), (w, h)))
        
        self.selector_rect = Rect(
            12*w /32, 16*h /64,
            9*w /32,  9*h /64
        )
        button_w, button_h = w * .5, 50
        self.confirm_button = Button(self.game, Rect(
            self.rect.left + (self.rect.width - button_w)/2, self.rect.top + self.rect.height - 2* button_h,
            button_w, button_h
        ), "BUY", "no", lambda: self.buy())

        self.do_freeze= freeze_game
        self.set_freezing(freeze_game, True)
    def buy(self):
        if not (self.active and self.active_item): return
        item_price = self.content[self.active_item]
        if item_price > self.game.player.balance: return
        if self.game.DEV_MODE:
            print(f"Player has bought {self.active_item.identifier} at ${item_price}.")

        self.game.player.gain(-item_price)
        self.game.player.inventory_bar.modify_amount(self.active_item, 1)
        self.game.marked.bought.append((type(self.active_item), item_price))
        self.active= False
    def get_texture(self):
        gui = self.background.copy()
        if self.active_item:
            mask= Surface(self.selector_rect.size)
            mask.fill((0, 0, 0))

            item_texture = transform.scale(self.active_item.texture, self.selector_rect.size)

            item_price = self.content[self.active_item]

            price_surface, price_rect= TEXT_FONT.render(f"${round(item_price, 2)}", size= 15)
            price_box_rect = Rect(
                (self.rect.width - price_rect.width)/2, self.selector_rect.bottom + price_rect.height,
                *price_rect.size
            )
            
            gui.blits((
                (mask, self.selector_rect.topleft),
                (item_texture, self.selector_rect.topleft),
                (price_surface, price_box_rect.topleft)
            ))
            self.confirm_button.change_type("yes" if item_price <= self.game.player.balance else "no")
            gui.blit(
                self.confirm_button.get_texture(),
                (
                    self.confirm_button.rect.left - self.rect.left,
                    self.confirm_button.rect.top - self.rect.top
                )
            )
        else:
            self.confirm_button.active= False
        return gui
    def on_click(self):
        mx, my = mouse.get_pos()
        translate_x, translate_y = self.rect.topleft
        if(
            translate_x + self.selector_rect.left <= mx <= translate_x + self.selector_rect.right
            and translate_y + self.selector_rect.top <= my <= translate_y + self.selector_rect.bottom
        ):
            self.confirm_button.active= False
            self.child_page = Selector(self.game, list(self.content.keys()))
            selected = self.child_page.get()
            self.set_freezing(self.do_freeze, True)
            self.child_page = None
            if not selected: return
            self.active_item= selected
            self.confirm_button.active= True
    def on_end(self):
        self.set_freezing(False, True)