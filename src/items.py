from pygame import Surface
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
        pass
    @property
    def texture(self) -> Surface:
        return self._texture if type(self._texture) == Surface else get_texture("items", self._texture)

class DiamondIngot(Item):
    def __init__(self, game):
        from blocks import DiamondGenerator
        super().__init__(game, "diamond_ingot", 20)
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

class IronIngot(Item):
    def __init__(self, game):
        from blocks import IronGenerator
        super().__init__(game, "iron_ingot", 5)
        self.crafts= [
            {IronGenerator: []}
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
