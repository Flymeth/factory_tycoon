from direction_sys import Direction
from items import Item
from random import random, choice

class Block:
    def __init__(self, game, type: str, inputs: Direction.typeof= Direction.fast(), outputs: Direction.typeof= Direction.fast(), texture= "default_block_texture", decorative=False, default_level= 1, max_level= 20) -> None:
        from items import Item
        from _main import Game

        self.game: Game= game
        self.type= type
        self.input= inputs
        self.output= outputs
        self.locked= False
        self.connected: dict[str, list[Block]]= {
            "in": [],
            "out": []
        }
        self.facing: int= Direction.South
        self.deletable= not decorative
        self.interactable= not decorative
        self.requires_update= not decorative
        self.texture= texture
        self.level= {
            "now": default_level,
            "max": default_level if decorative else max_level
        }
        self.requires_maintenance= False
        self.processing_items: list[Item] = []
        self.processed_items: list[Item] = []
        self.next_item_output: Direction.typeof = Direction.fast("a") # Si la sortie du prochain item doit être choisie, sinon cela prendre une sortie au hazard parmis la liste des sorties
        pass
    @property
    def position(self) -> tuple[int, int]:
        found= self.game.map.find_blocks(lambda block: block == self)
        assert len(found) == 1, "Block isn't in the map or in double"
        return found[0][0]
    def exec(self):
        pass
    def draw(self):
        pass
    def __str__(self) -> str:
        return self.type[0].upper()

class EmptyBlock(Block):
    def __init__(self, game) -> None:
        super().__init__(game, "empty", texture= "empty", decorative= True)
        pass

class GlobalSeller(Block):
    def __init__(self, game) -> None:
        super().__init__(game, "global_seller", inputs= Direction.fast("a"), texture= "global_seller", max_level= 1)
        pass
    def exec(self):
        item= self.processing_items.pop(0)
        self.game.player.sell(item)
class Seller(Block):
    def __init__(self, game, sell_type: list[Item]= []) -> None:
        super().__init__(game, "seller", inputs= Direction.fast("a"), texture= "seller", max_level= 1)
        self.accept= sell_type
    def exec(self):
        if self.requires_maintenance: return

        item = self.processed_items[0] # Pas de pop() car si l'item est invalide on le laisse dans la machine
        if item in self.accept:
            self.processed_items.pop(0)
            item_value= item.value * (self.game.marked.courts.get(item.name) or 1)
            self.game.player.gain(item_value)
        else:
            self.requires_maintenance= True

class Trash(Block):
    def __init__(self, game) -> None:
        super().__init__(game, "trash", Direction.fast("a"))
    def exec(self):
        self.processing_items= []

class Generator(Block):
    def __init__(self, game, ingot_type: Item, ingot_spawn_chance: float = .35, texture: str = "default_generator") -> None:
        assert 0 <= ingot_spawn_chance <= 1, "Spawn change must be between 0 and 1 included"
        
        from items import Cobble
        super().__init__(game, "generator", outputs= Direction.fast("a"), texture= texture)
        self.ingot = ingot_type
        self.others: list[Item]= [Cobble]
        self.spawn_chance= ingot_spawn_chance
    def exec(self):
        self.processing_items.append(
            (self.ingot if random() <= self.spawn_chance else choice(self.others)) # Ici on séléctionne la classe adécquate
            (self.game) # Et ici on instancie cette classe
        )
        return super().exec()

class DiamondGenerator(Generator):
    def __init__(self, game) -> None:
        from items import DiamondIngot
        super().__init__(game, ingot_type= DiamondIngot, ingot_spawn_chance=.25, texture= "gold_generator")
    
class GoldGenerator(Generator):
    def __init__(self, game) -> None:
        from items import GoldIngot
        super().__init__(game, ingot_type= GoldIngot, texture= "gold_generator")

class IronGenerator(Generator):
    def __init__(self, game) -> None:
        from items import IronIngot
        super().__init__(game, ingot_type= IronIngot, texture= "iron_generator")

class Sorter(Block):
    def __init__(self, game, valid_items: list[Item]= []) -> None:
        super().__init__(game, type, inputs= Direction.fast("n"), outputs= Direction.fast("se"), texture= "sorter", max_level= 5)
        self.valid= valid_items
    def exec(self):
        item = self.processing_items.pop(0)
        if item in self.valid:
            self.next_item_output = Direction.fast("s")
        else:
            self.next_item_output = Direction.fast("e")
        self.processed_items.append(item)
        

if __name__ == "__main__":
    pass