from pygame import Surface, BLEND_RGBA_MULT, PixelArray
from textures import get_texture

next_item_id= 0
class Item:
    def __init__(self, game, name: str, value: float, texture: str | Surface = "") -> None:
        global next_item_id
        from blocks import Block
        from _main import Game

        self.game: Game= game
        self.id= next_item_id
        next_item_id+= 1

        self.name= name
        self.value= value
        self._texture= texture if type(texture) == Surface else (texture or name.lower())
        self.crafts: list[dict[Block, list[Item]]] = []
        """ A list of dictionaries in which:
                Keys are the block that can craft this item
                Value are a list of items that the block requires to create this item
        """

        self.temperature: float = 0
        """Value must be between 0 and 1 included"""

        temperature_layer_color = (248, 67, 18)
        normal_texture= self.texture
        self.temperature_texture= normal_texture.copy()
        pxarr = PixelArray(self.temperature_texture)
        dimentions: tuple[int, int] = pxarr.shape
        for x in range(dimentions[0]):
            for y in range(dimentions[1]):
                if normal_texture.get_at((x, y)).a:
                    pxarr[x, y] = temperature_layer_color
        pxarr.close()
    @property
    def texture(self) -> Surface:
        texture= (
            self._texture if type(self._texture) == Surface else get_texture("items", self._texture)
        ).copy()
        if self.temperature and getattr(self, "temperature_texture", None):
            self.temperature_texture.set_alpha(150 * self.temperature)
            texture.blit(self.temperature_texture, (0, 0))
        return texture


class DiamondIngot(Item):
    def __init__(self, game):
        from blocks import DiamondGenerator
        super().__init__(game, "diamond", 20)
        self.crafts= [
            {DiamondGenerator: []}
        ]

class GoldIngot(Item):
    def __init__(self, game):
        from blocks import GoldGenerator
        super().__init__(game, "gold_ingot", 10)
        self.crafts= [
            {GoldGenerator: []}
        ]

class GoldPlate(Item):
    def __init__(self, game) -> None:
        from blocks import Press

        super().__init__(game, "gold_plate", 20)
        self.crafts= [
            {Press: [GoldIngot]}
        ]

class IronIngot(Item):
    def __init__(self, game):
        from blocks import IronGenerator
        super().__init__(game, "iron_ingot", 5)
        self.crafts= [
            {IronGenerator: []}
        ]

class IronPlate(Item):
    def __init__(self, game) -> None:
        from blocks import Press

        super().__init__(game, "iron_plate", 10)
        self.crafts= [
            {Press: [IronIngot]}
        ]

class Stone(Item):
    def __init__(self, game) -> None:
        from blocks import Generator
        super().__init__(game, "stone", 1)
        self.crafts= [
            {Generator: []}
        ]

if __name__ == "__main__":
    print({Stone(None).id: "hello"})
