from quests import Quest
from blocks import Block, Trash, GlobalSeller
from items import Item
from gui import InventoryBar
from pygame import MOUSEBUTTONDOWN, mouse

class Player:
    def __init__(self, game, name: str, default_credits= 0, default_quests: list[Quest]= []) -> None:
        from _main import Game

        self.game: Game= game
        self.name= name
        self.credits= default_credits
        self.active_quests= default_quests
        self.achieved_quests: list[Quest]= []
        self.selled: list[Item]= []

        self.inventory_bar = InventoryBar(game, [Trash(game), GlobalSeller(game)])
        self.inventory_bar.selected= 0

        self.game.add_event(MOUSEBUTTONDOWN, lambda g, e: self.clicked(e.button))
        pass
    def gain(self, amount: float) -> float:
        self.credits+= amount
        return self.credits
    def clicked(self, button: int):
        if not button in (1, 3): return # 1 = left click; 3 = right click
        mouse_position= mouse.get_pos()
        navbar_rect= self.inventory_bar.get_rect()
        print(mouse_position, navbar_rect)
        if(
            len([None for i in range(2)
                if navbar_rect["position"][i] <= mouse_position[i] <= navbar_rect["position"][i] + navbar_rect["size"][i]
            ]) == 2
        ):
            return self.inventory_bar.change_selected_item(*mouse_position)
        else:
            if button == 1:
                self.place()
            else: self.remove()
    def place(self):
        assert self.game, "Cannot perform this action because the game object is required"
        assert self.inventory_bar.selected >= 0, "Player has not selected an item"
        coordonates = self.game.cam.get_cursor_coordonates()
        assert coordonates, "Invalid cursor position"
        self.game.map.place(self.inventory_bar.get_selected_block(), coordonates)
    def remove(self):
        assert self.game, "Cannot perform this action because the game object is required"
        self.game.map.delete(self.game.cam.get_cursor_coordonates())