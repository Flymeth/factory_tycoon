from typing import Any
from pygame import Surface, Rect, transform, display
from fonts import TEXT_FONT
from gui._assets import GUI

class InventoryItem():
    def __init__(self, game, amount: int, item: Any, rect: Rect) -> None:
        from blocks import Block
        from _main import Game

        self.game: Game = game
        self.item: Block= item
        self.amount= amount
        self.rect= rect
        self.selected= False
    @property
    def texture(self):
        texture= transform.scale(
            self.item.texture,
            self.rect.size
        )
        
        if not self.selected: texture.set_alpha(120)
        if not self.amount: texture.set_alpha(50)
        
        amount_text, amount_rect = TEXT_FONT.render(str(self.amount), fgcolor= (255, 255, 255), size= 15)
        texture.blit(amount_text, (self.rect.width - amount_rect.width - 2, self.rect.height - amount_rect.height - 2))
        return texture
    def take_one(self):
        """ This method does not change items amount
        """
        if self.amount < 0: return
        block = self.item
        self.item= block.duplicate()
        return block

class InventoryBar(GUI):
    def __init__(self, game, content: list[tuple[Any, int]] = []) -> None:
        from _main import Game

        self.game: Game= game
        self.selected: int = -1
        self.items_size= 50
        self.paddings= 5
        self.items: list[InventoryItem]= []

        for block, amount in content:
            self.modify_amount(block, amount)
        rect= self.__get_rect__()
        super().__init__(game, rect, Surface(rect.size))
        pass
    def __get_rect__(self) -> Rect:
        window_size = display.get_window_size()
        width, height = (
            self.paddings + len(self.items) * (self.items_size + self.paddings),
            self.paddings *2 + self.items_size
        )
        return Rect((window_size[0] - width)/2, window_size[1] - (height + self.paddings), width, height)
    def __update_items_rect__(self) -> None:
        for index, item in enumerate(self.items):
            x, y = (
                self.paddings + index * (self.items_size + self.paddings),
                self.paddings
            )
            item.rect= Rect(x, y, self.items_size, self.items_size)
    def get_selected_item(self) -> InventoryItem | None:
        """ Returns the block's instance of the selected block
        """
        for item in self.items:
            if item.selected:
                return item
    def set_selected_item(self, index: int) -> bool:
        if not self.items[index].amount: return False
        done= False
        for i, item in enumerate(self.items):
            item.selected= index == i
            done|= item.selected
        return done
    def modify_amount(self, block: Any, add: int):
        for item in self.items:
            if type(item.item) == type(block):
                item.amount= max(0, item.amount + add)
                return
        # If python reach this point, that means that the item is not in the inventory, so we add it
        self.items.append(InventoryItem(self.game, max(0, add), block, None))
        self.__update_items_rect__()
        self.rect= self.__get_rect__()
    def get_texture(self):
        gui= transform.scale(self.background, self.rect.size)
        for item in self.items:
            gui.blit(item.texture, item.rect.topleft)
        return gui