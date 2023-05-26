from quests import Quest
from blocks import Trash, GlobalSeller, Convoyer, Sorter, Generator
from items import Item
from gui import InventoryBar
from pygame import MOUSEBUTTONDOWN, mouse, KEYDOWN, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_a, K_r, K_e

keys_index = (K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9)
fast_edit_key= K_a
rotate_key= K_r
edit_key= K_e

class Player:
    def __init__(self, game, name: str, default_credits= 0, default_quests: list[Quest]= []) -> None:
        from _main import Game

        self.game: Game= game
        self.name= name
        self.credits= default_credits
        self.active_quests= default_quests
        self.achieved_quests: list[Quest]= []
        self.selled: list[Item]= []

        self.inventory_bar = InventoryBar(game, [Trash(game), GlobalSeller(game), Convoyer(game), Sorter(game), Generator(game)])
        self.inventory_bar.selected= 0

        self.game.add_event(MOUSEBUTTONDOWN, lambda g, e: self.clicked(e.button))
        self.game.add_event(KEYDOWN, lambda g, e: self.key_pressed(e.key))
        pass
    def gain(self, amount: float) -> float:
        self.credits+= amount
        return self.credits
    def key_pressed(self, key: int):
        if key in keys_index:
            index= keys_index.index(key)
            if index >= len(self.inventory_bar.content): return
            self.inventory_bar.selected= index
            if self.game.DEV_MODE:
                print(f"ITEM INDEX SET TO {index}.")
            return
        
        cursor= self.game.cam.get_cursor_coordonates()
        block = self.game.map.get_block(*cursor)
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
        if actualisation_required:
            self.game.map.actualize(cursor)
    def clicked(self, button: int):
        if not button in (1, 3): return # 1 = left click; 3 = right click
        mouse_position= mouse.get_pos()
        navbar_rect= self.inventory_bar.get_rect()
        if self.game.DEV_MODE:
            print("CLICKED POSITION & GUI RECT:")
            print(mouse_position, navbar_rect)

        if(
            len([None for i in range(2)
                if navbar_rect["position"][i] <= mouse_position[i] <= navbar_rect["position"][i] + navbar_rect["size"][i]
            ]) == 2
        ):
            gui_mouse_position_x = mouse_position[0] - navbar_rect["position"][0]
            index = gui_mouse_position_x // (self.inventory_bar.items_size + self.inventory_bar.paddings/2)
            if index >= len(self.inventory_bar.content): return
            if self.game.DEV_MODE:
                print(f"ITEM INDEX SET TO {index}.")
            self.inventory_bar.selected = int(index)
        else:
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
        self.game.map.place(self.inventory_bar.get_selected_block(), coordonates)
    def remove(self):
        assert self.game, "Cannot perform this action because the game object is required"
        self.game.map.delete(self.game.cam.get_cursor_coordonates())