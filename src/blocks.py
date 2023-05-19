from direction_sys import Direction
from items import Item
from random import random, choice
from textures import get_texture
from pygame import transform

class Block:
    def __init__(self, game, identifier: str, inputs: Direction.multiple= Direction.fast(), outputs: Direction.multiple= Direction.fast(), texture= "default_block_texture", decorative=False, default_level= 1, max_level= 20, right_rotations: int = 0) -> None:
        from items import Item
        from _main import Game

        self.game: Game= game
        self.identifier= identifier
        self.inputs= inputs
        self.outputs= outputs
        self.locked= False
        self.connected: dict[str, list[tuple[int, Block]]]= {
            "in": [],
            "out": []
        }
        """
        Better typage:

        {
            "in": (`<input_index>`, Block)[],
            "out": (`<output_index>`, Block)[]
        }

        Where:
            - `<input_index>` is the index of the input connection in the `self.inputs` list
            - `<output_index>` is the index of the output connection in the `self.outputs` list
        """
        
        self.right_rotations: int= right_rotations %4
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
        self.block_bellow: Block | None= None
        pass
    @property
    def position(self) -> tuple[int, int]:
        """ Returns the block position in the map matrice
        """
        assert self.game, "Cannot calculate position without the game object"
        found= self.game.map.find_blocks(lambda block: block == self)
        assert len(found) == 1, "Block isn't in the map or has been added twice"
        return found[0][0]
    def exec(self):pass
    def draw(self):
        assert self.game, "Cannot draw block without the game object"
        angle= self.right_rotations * 90
        texture= transform.scale(
            transform.rotate(get_texture("blocks", self.texture), angle),
            [self.game.cam.zoom] *2
        )
        x, y= self.game.cam.get_screen_position(self.position)
        self.game.pygame.screen.blit(texture, (x, y))
        pass
    def __str__(self) -> str:
        return self.identifier[0].upper()

class Seller(Block):
    def __init__(self, game, sell_type: list[Item]= []) -> None:
        super().__init__(game, identifier= "seller", inputs= Direction.fast("a"), texture= "seller", max_level= 1)
        self.accept= sell_type
    def exec(self):
        if self.requires_maintenance: return

        item = self.processed_items[0] # Pas de pop() car si l'item est invalide on le laisse dans la machine
        if not self.accept or item in self.accept:
            self.processed_items.pop(0)
            self.game.player.selled.append(item)
            
            item_value= item.value * (self.game.marked.courts.get(item.name) or 1)
            self.game.player.gain(item_value)
        else:
            self.requires_maintenance= True
class GlobalSeller(Seller):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.identifier= "global_seller"
        self.texture= "global_seller"
        pass

class Trash(Block):
    def __init__(self, game) -> None:
        super().__init__(game, identifier= "trash",  inputs= Direction.fast("a"))
    def exec(self):
        self.processing_items= []

class Generator(Block):
    def __init__(self, game, ingot_type: Item, ingot_spawn_chance: float = .35, texture: str = "default_generator") -> None:
        assert 0 <= ingot_spawn_chance <= 1, "Spawn change must be between 0 and 1 included"
        
        from items import Cobble
        super().__init__(game, "generator", outputs= Direction.fast("a"), texture= texture)
        self.extracts = ingot_type
        self.others: list[type[Item]]= [Cobble]
        self.spawn_chance= ingot_spawn_chance
    def exec(self):
        self.processing_items.append(
            (self.extracts if random() <= self.spawn_chance else choice(self.others)) # Ici on séléctionne la classe adécquate
            (self.game) # Et ici on instancie cette classe
        )
        return super().exec()

class DiamondGenerator(Generator):
    def __init__(self, game) -> None:
        from items import DiamondIngot
        super().__init__(game, ingot_type= DiamondIngot(game), ingot_spawn_chance=.25, texture= "gold_generator")
    
class GoldGenerator(Generator):
    def __init__(self, game) -> None:
        from items import GoldIngot
        super().__init__(game, ingot_type= GoldIngot(game), texture= "gold_generator")

class IronGenerator(Generator):
    def __init__(self, game) -> None:
        from items import IronIngot
        super().__init__(game, ingot_type= IronIngot(game), texture= "iron_generator")

class Sorter(Block):
    def __init__(self, game, valid_items: list[Item]= []) -> None:
        super().__init__(game, "sorter", inputs= Direction.fast("n"), outputs= Direction.fast("se"), texture= "sorter", max_level= 5)
        self.valid= valid_items
    def exec(self):
        item = self.processing_items.pop(0)
        if not self.valid or item in self.valid:
            self.next_item_output = Direction.fast("s")
        else:
            self.next_item_output = Direction.fast("e")
        self.processed_items.append(item)

class FloorBlock(Block):
    def __init__(self, game, identifier: str, texture="default_floor_texture") -> None:
        super().__init__(game, identifier= identifier, texture= texture, decorative= True)

class EmptyBlock(FloorBlock):
    def __init__(self, game) -> None:
        super().__init__(game, "empty", "empty")
        pass
class MineBlock(FloorBlock):
    def __init__(self, game, mine_type: Item) -> None:
        super().__init__(game, "mine", "mine")
        self.ressource= mine_type

if __name__ == "__main__":
    t=Trash(None)
    s=Sorter(None)
    pass