from blocks import Block
from pygame import surface, display, transform

class InventoryBar():
    def __init__(self, game, content: list[Block] = []) -> None:
        from _main import Game

        self.game: Game= game
        self.content= content
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
