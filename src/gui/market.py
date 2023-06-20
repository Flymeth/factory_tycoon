from typing import Any
from pygame import display, Rect, transform, mouse, Surface
from gui.selector import Selector
from gui._assets import Button, Page
from textures import get_texture
from fonts import TEXT_FONT, TITLE_FONT_BOLD, auto_wrap

class MarketGUI(Page):
    def __init__(self, game, sellable: dict[Any, float], freeze_game: bool = True) -> None:
        from blocks import Block

        self.content: dict[Block, float] = sellable
        self.active= False
        self.active_item: Block | None= None

        # GUI Rect Set
        win_size= display.get_window_size()
        texture= get_texture("uis", "market")
        texture_rect= texture.get_rect()
        
        gui_height= win_size[1] - 50
        gui_width = texture_rect.width * gui_height/texture_rect.height
        x, y = [
            (win_size[i] - (gui_width, gui_height)[i])/2
            for i in range(2)
        ]
        super().__init__(game, Rect(x, y, gui_width, gui_height), texture)
        
        INIT_GUI_PIXELS= texture.get_rect().size
        INIT_GUI_BUTTON_POSITION= (18, 16)
        INIT_GUI_BUTTON_SIZE= (9, 9)
        self.selector_rect = Rect(
            INIT_GUI_BUTTON_POSITION[0]*gui_width /INIT_GUI_PIXELS[0],
            INIT_GUI_BUTTON_POSITION[1]*gui_height /INIT_GUI_PIXELS[1],
            INIT_GUI_BUTTON_SIZE[0]*gui_width /INIT_GUI_PIXELS[0],
            INIT_GUI_BUTTON_SIZE[1]*gui_height /INIT_GUI_PIXELS[1]
        )
        button_w = min(200, gui_width * .5)
        button_h = button_w/3
        self.confirm_button = Button(self.game, Rect(
            self.rect.left + (self.rect.width - button_w)/2, self.rect.bottom - button_h - 20,
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
            mask.fill((30,) * 3)

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
        
        # Titles and sub
        title, title_rect= TITLE_FONT_BOLD.render("The Shop", size= 30)
        sub, sub_rect = auto_wrap(TEXT_FONT, 15, "Click on the item to modify your selection".upper(), self.rect.width /2, 'center', paragraphes_spacement= 5)

        gui.blits((
            (title, ((self.rect.width - title_rect.width)/2, 20)),
            (sub, ((self.rect.width - sub_rect.width)/2, self.rect.centery))
        ))
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