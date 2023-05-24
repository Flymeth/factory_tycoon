from uuid import uuid1
from pygame import Surface
from textures import get_texture

class Item:
    def __init__(self, game, name: str, value: float, texture: str | Surface = "") -> None:
        from blocks import Block
        from _main import Game

        self.game: Game= game
        self.id= uuid1()
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

class Cobble(Item):
    def __init__(self, game) -> None:
        from blocks import Generator
        super().__init__(game, "cobble", 1)
        self.crafts= [
            {Generator: []}
        ]

if __name__ == "__main__":
    print({Cobble(None).id: "hello"})
