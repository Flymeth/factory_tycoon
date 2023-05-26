from pygame import surface, display, transform, MOUSEBUTTONDOWN
from typing import Any

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
        """ Return the rect of the gui
            {
                "size": tuple[float],
                "position": tuple[float]
            }
        """
        window_size = display.get_window_size()
        width, height = (
            self.paddings + len(self.content) * (self.items_size + self.paddings),
            self.paddings *2 + self.items_size
        )
        return {
            "size": (width, height),
            "position": (
                window_size[0]/2 - width/2,
                window_size[1] - (height + self.paddings)
            )
        }
    def draw(self):
        assert self.game, "Cannot draw without the game object"

        rect = self.get_rect()
        gui= surface.Surface(rect["size"])
        
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

        self.game.pygame.screen.blit(gui, rect["position"])

class Selector():
    def __init__(self, game, choices: list[Any], freeze_game= False) -> None:
        from _main import Game
        from items import Item
        from blocks import Block

        self.game: Game= game
        self.choices= choices
        self.choosed: Block | Item | None= None
        self.scrollDown= 0

        if freeze_game:
            self.game.freeze_process = self.game.cam.freeze_position = self.game.cam.freeze_zoom = True
        self.active= False

        self.game.add_event(MOUSEBUTTONDOWN, lambda g, e: self.clicked())
        pass
    def update(self):
        
        pass
    def clicked(self):
        if not self.active: return
        self.choosed= self.choices[0]
    def get(self) -> Any | None:
        self.active= True
        while not (self.choosed or self.game.update()):
            self.update()
        return self.choosed
    def unfreeze(self):
        self.game.freeze_process = self.game.cam.freeze_position = self.game.cam.freeze_zoom = False