from quests import Quest
from blocks import Trash, GlobalSeller, Convoyer, Sorter, Generator, Connecter, FloorBlock, Smelter, Press
from items import Item
from gui.inventory_bar import InventoryBar
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, mouse, KEYDOWN, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_a, K_m, K_r, K_e, K_DOLLAR, display, transform, Rect
from fonts import TITLE_FONT_BOLD
from textures import get_texture
from typing import Literal, Callable
from custom_events_identifier import DRAW_EVENT, TICK_EVENT

keys_index = (K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9)
fast_edit_key= K_a
rotate_key= K_r
edit_key= K_e
market_key= K_m
cheat_console_key= K_DOLLAR

class Player:
    def __init__(self, game, name: str, default_balance= 0, quests_to_achieve: list[type[Quest]]= []) -> None:
        from _main import Game

        self.game: Game= game
        self.name= name
        self.balance: float= default_balance
        self.quests= quests_to_achieve
        self.active_quest: Quest | None = None
        self.achieved_quests: list[Quest]= []
        self.selled: list[Item]= []
        self.__is_clicking: list[int]= []

        self.inventory_bar = InventoryBar(game, [
            (Generator(game), 10), (Convoyer(game), 200), (GlobalSeller(game), 1)
        ])
        self.inventory_bar.set_selected_item(0)

        self.game.add_event(MOUSEBUTTONDOWN, lambda g, e: self.__set_clicking__(True, e.button))
        self.game.add_event(MOUSEBUTTONUP, lambda g, e: (
            self.__set_clicking__(False, e.button), self.clicked(e.button)
        ))
        self.game.add_event(KEYDOWN, lambda g, e: self.key_pressed(e.key))
        self.game.add_event(DRAW_EVENT, lambda g, e: (
            self.draw_blockVisualisation(), self.inventory_bar.draw(), self.draw_hud(), self.handle_long_click()
        ), only_for_scenes= ["ingame"])
        self.game.add_event(TICK_EVENT, lambda g, e: self.quest_updator(), only_for_scenes= ["ingame"])

        self.uis: list[Callable[[], Rect]] = [lambda: self.inventory_bar.rect]
        self.freeze_blocks_interaction= False
        pass
    def __set_clicking__(self, active: bool, btn: int):
        is_containing= btn in self.__is_clicking
        if is_containing and not active:
            self.__is_clicking.remove(btn)
        elif active and not is_containing:
            self.__is_clicking.append(btn)
    def next_quest(self, success: bool= False):
        if success:
            self.active_quest.give_reward()
            self.achieved_quests.append(self.active_quest)

        next_quest_index = self.quests.index(self.active_quest.__class__) +1
        if next_quest_index >= len(self.quests):
            self.quests= []
            self.active_quest= None
        else: self.active_quest= self.quests[next_quest_index](self.game)
    def quest_updator(self):
        if not self.quests: return
        if not self.active_quest:
            self.active_quest= self.quests[0](self.game)
            self.uis.append(lambda: self.active_quest.get_surface()[1])
        
        self.active_quest.update_pourcentage()
        if self.active_quest.check_success():
            self.next_quest(True)
    def gain(self, amount: float) -> float:
        self.balance+= amount
        if self.game.DEV_MODE:
            print(f"NEW PLAYER BALANCE: {self.balance}")
        return self.balance
    def key_pressed(self, key: int):
        if key in keys_index:
            index= keys_index.index(key)
            if index >= len(self.inventory_bar.items): return
            self.inventory_bar.set_selected_item(index)
            if self.game.DEV_MODE:
                print(f"ITEM INDEX SET TO {index}.")
            return
        elif key == market_key:
            try:
                self.game.marked.open_market()
            except AssertionError as err:
                if self.game.DEV_MODE:
                    print(f"Cannot open the market:\n{err}")
            return
        elif key == cheat_console_key:
            note_msg= "(Note: to modify data, use the setattr(<object>, <property_name>, <value>) function.)"
            print(note_msg, "/" + "-"*len(note_msg), sep= "\n")
            cheat= input("|[FT-CHEAT-CONSOLE]>>> ")
            try:
                __GAME__= self.game
                ans= eval(cheat)
                print(f"|[FT-CHEAT-CONSOLE]:\n{ans}")
            except Exception as err:
                print(f"|[FT-CHEAT-CONSOLE]<ERROR>:\n{err}")
            print("\\" + "-"*len(note_msg))
            return
        
        if self.freeze_blocks_interaction: return
        cursor= self.game.cam.get_cursor_coordonates()
        block = self.game.map.get_block(*cursor)
        is_visualisationBlock= False
        if isinstance(block, FloorBlock):
            block= self.inventory_bar.get_selected_item().item
            is_visualisationBlock= True
        if not block: return
        actualisation_required= False
        if key == fast_edit_key:
            if not  getattr(block, "fast_edit", False): return
            actualisation_required= block.fast_edit()
        elif key == edit_key:
            actualisation_required= block.edit()
        elif key == rotate_key:
            if block.rotable:
                block.right_rotations= (block.right_rotations +1)% 4
                actualisation_required= True
        if actualisation_required and not is_visualisationBlock:
            self.game.map.actualize(cursor)
    def mouse_pos_type(self) -> Literal["block", "ui"]:
        x, y = mouse.get_pos()
        for getter in self.uis:
            rect= getter()
            if(
                rect.left <= x <= rect.left + rect.width
                and  rect.top <= y <= rect.top + rect.height
            ):
                return "ui"
        return "block"
    def handle_long_click(self):
        if not self.__is_clicking: return
        if self.freeze_blocks_interaction or self.mouse_pos_type() != "block": return
        button= self.__is_clicking[0]
        if not button in (1, 3): return # 1 = left click; 3 = right click

        if self.game.DEV_MODE:
            print(f"ACTION: {'placed' if button == 1 else 'removed'} block.")
        try:
            if button == 1:
                self.place()
            else: self.remove()
        except AssertionError as err:
            if self.game.DEV_MODE:
                print("ERROR WHEN WANTING TO DO THIS ACTION:")
                print(err)
    def clicked(self, button: int):
        if self.freeze_blocks_interaction or self.mouse_pos_type() != "ui": return
        if button != 1: return # 1 = left click
        mx, my= mouse.get_pos()
        navbar_rect= self.inventory_bar.rect
        if self.game.DEV_MODE:
            print("CLICKED POSITION & GUI RECT:")
            print((mx, my), navbar_rect)

        if(
            navbar_rect.left <= mx <= navbar_rect.right
            and navbar_rect.top <= my <= navbar_rect.bottom
        ):
            gui_mouse_position_x = mx - navbar_rect.topleft[0]
            index = gui_mouse_position_x // (self.inventory_bar.items_size + self.inventory_bar.paddings)
            if index >= len(self.inventory_bar.items):
                return
            if self.inventory_bar.set_selected_item(index) and self.game.DEV_MODE:
                print(f"ITEM INDEX SET TO {index}.")
    def place(self):
        assert self.game, "Cannot perform this action because the game object is required"
        coordonates = self.game.cam.get_cursor_coordonates()
        assert coordonates, "Invalid cursor position"
        item = self.inventory_bar.get_selected_item()
        assert item, "Player has not selected an item"
        assert item.amount, "Player has not enought of this item"
        placed= self.game.map.place(item.take_one(), coordonates)
        if placed:
            self.inventory_bar.modify_amount(item.item, -1)
    def remove(self):
        assert self.game, "Cannot perform this action because the game object is required"
        block = self.game.map.delete(self.game.cam.get_cursor_coordonates())
        self.inventory_bar.modify_amount(block, 1)
    def draw_blockVisualisation(self):
        if self.game.cam.moving_camera or self.freeze_blocks_interaction or self.mouse_pos_type() != "block": return

        coordonates= self.game.cam.get_cursor_coordonates()
        current_block= self.game.map.get_block(*coordonates)
        if not isinstance(current_block, FloorBlock): return

        selected = self.inventory_bar.get_selected_item()
        if not selected: return
        block, amount = selected.item, selected.amount
        if not amount: return
        block._cache_coordonates= coordonates
        rect = block.get_rect()
        if not rect: return False
        texture= transform.scale(block.postprocessing(block.get_surface()), rect.size)
        texture.set_alpha(255//4)

        self.game.draw(texture, rect.topleft)
    def draw_hud(self):
        window_size= display.get_window_size()

        # Balance
        balance_text_size= window_size[0] // 50
        balance_text_padding= balance_text_size
        balance_text, balance_rect= TITLE_FONT_BOLD.render(f"Balance: ${round(self.balance, 2)}", fgcolor= (0, 0, 0), size= balance_text_size)
        balance_bg_texture= get_texture("uis", "balance_bg")
        balance_bg= transform.scale(balance_bg_texture, (
            balance_rect.width + balance_text_padding *2,
            balance_rect.height + balance_text_padding *2
        ))
        balance_bg_rect= balance_bg.get_rect()
        balance_bg.blit(balance_text, [
            (getattr(balance_bg_rect, prop) - getattr(balance_rect, prop))/2
            for prop in ("width", "height")
        ])

        self.game.draw(balance_bg, ((window_size[0] - balance_bg_rect.width)/2, 0))

        # Current Quest
        if self.active_quest:
            self.active_quest.draw()
        pass