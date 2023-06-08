from quests import Quest
from blocks import Trash, GlobalSeller, Convoyer, Sorter, Generator, Connecter, FloorBlock
from items import Item
from gui import InventoryBar
from pygame import MOUSEBUTTONDOWN, mouse, KEYDOWN, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_a, K_r, K_e, display, transform, Rect
from fonts import TITLE_FONT_BOLD
from textures import get_texture
from typing import Literal
from custom_events_identifier import DRAW_EVENT, TICK_EVENT

keys_index = (K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9)
fast_edit_key= K_a
rotate_key= K_r
edit_key= K_e

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

        self.inventory_bar = InventoryBar(game, [(Generator(game), 10), (Convoyer(game), 200), (GlobalSeller(game), 1)])
        self.inventory_bar.selected= 0

        self.game.add_event(MOUSEBUTTONDOWN, lambda g, e: self.clicked(e.button))
        self.game.add_event(KEYDOWN, lambda g, e: self.key_pressed(e.key))
        self.game.add_event(DRAW_EVENT, lambda g, e: (
            self.draw_blockVisualisation(), self.inventory_bar.draw(), self.draw_hud()
        ))
        self.game.add_event(TICK_EVENT, lambda g, e: self.quest_updator())

        self.uis_rects: list[Rect] = [self.inventory_bar.get_rect()]
        self.freeze_blocks_interaction= False
        pass
    def quest_updator(self):
        if not self.quests: return
        if not self.active_quest:
            self.active_quest= self.quests[0](self.game)
        
        self.active_quest.update_pourcentage()
        if self.active_quest.check_success():
            self.active_quest.give_reward()
            self.achieved_quests.append(self.active_quest)

            next_quest_index = self.quests.index(self.active_quest.__class__) +1
            if next_quest_index >= len(self.quests):
                self.quests= []
                self.active_quest= None
            else: self.active_quest= self.quests[next_quest_index](self.game)
    def gain(self, amount: float) -> float:
        self.balance+= amount
        if self.game.DEV_MODE:
            print(f"NEW PLAYER BALANCE: {self.balance}")
        return self.balance
    def key_pressed(self, key: int):
        if key in keys_index:
            index= keys_index.index(key)
            if index >= len(self.inventory_bar.content): return
            self.inventory_bar.selected= index
            if self.game.DEV_MODE:
                print(f"ITEM INDEX SET TO {index}.")
            return
        
        if self.freeze_blocks_interaction: return
        cursor= self.game.cam.get_cursor_coordonates()
        block = self.game.map.get_block(*cursor)
        is_visualisationBlock= False
        if isinstance(block, FloorBlock):
            block= self.inventory_bar.content[self.inventory_bar.selected][0]
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
        for rect in self.uis_rects:
            if(
                rect.left <= x <= rect.left + rect.width
                and  rect.top <= y <= rect.top + rect.height
            ):
                return "ui"
        return "block"
    def clicked(self, button: int):
        if not button in (1, 3): return # 1 = left click; 3 = right click
        if self.freeze_blocks_interaction: return
        mouse_position= mouse.get_pos()
        navbar_rect= self.inventory_bar.get_rect()
        if self.game.DEV_MODE:
            print("CLICKED POSITION & GUI RECT:")
            print(mouse_position, navbar_rect)

        if(
            len([None for i in range(2)
                if navbar_rect.topleft[i] <= mouse_position[i] <= navbar_rect.topleft[i] + navbar_rect.size[i]
            ]) == 2
        ):
            gui_mouse_position_x = mouse_position[0] - navbar_rect.topleft[0]
            index = gui_mouse_position_x // (self.inventory_bar.items_size + self.inventory_bar.paddings)
            if index >= len(self.inventory_bar.content) or self.inventory_bar.content[index][1] == 0:
                return
            if self.game.DEV_MODE:
                print(f"ITEM INDEX SET TO {index}.")
            self.inventory_bar.selected = index
        elif self.mouse_pos_type() == "block":
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
    def place(self):
        assert self.game, "Cannot perform this action because the game object is required"
        assert self.inventory_bar.selected >= 0, "Player has not selected an item"
        coordonates = self.game.cam.get_cursor_coordonates()
        assert coordonates, "Invalid cursor position"
        block = self.inventory_bar.get_selected_block()
        if not block: return
        placed= self.game.map.place(block, coordonates)
        if placed:
            self.inventory_bar.modify_amount(block, -1)
    def remove(self):
        assert self.game, "Cannot perform this action because the game object is required"
        block = self.game.map.delete(self.game.cam.get_cursor_coordonates())
        self.inventory_bar.modify_amount(block, 1)
    def draw_blockVisualisation(self):
        if self.game.cam.moving_camera: return

        coordonates= self.game.cam.get_cursor_coordonates()
        current_block= self.game.map.get_block(*coordonates)
        if not isinstance(current_block, FloorBlock): return

        inv= self.inventory_bar
        block, amount = inv.content[inv.selected]
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
        balance_text, balance_rect= TITLE_FONT_BOLD.render(f"Balance: ${self.balance}", fgcolor= (0, 0, 0), size= balance_text_size)
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