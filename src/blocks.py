from direction_sys import Direction
from items import Item, Stone, GoldIngot
from random import random, choice
from textures import get_texture
from pygame import transform, display, Surface
from gui import Selector

class Block:
    def __init__(self, game, identifier: str, inputs: Direction.multiple= Direction.fast(), outputs: Direction.multiple= Direction.fast(), texture: str | Surface= "", decorative=False, default_level= 1, max_level= 20, right_rotations: int = 0, rotable: bool= True, update_each: int= 1000) -> None:
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
        
        self.rotable= rotable
        self.right_rotations: int= right_rotations %4
        self.deletable= not decorative
        self.interactable= not decorative
        self.requires_update= not decorative
        self._texture: str | Surface= texture
        self.level= {
            "now": default_level,
            "max": default_level if decorative else max_level
        }
        self.requires_maintenance= False
        self.processing_items: list[Item] = []
        self.processed_items: list[Item] = []
        self.next_item_output: Direction.typeof = Direction.fast("a") # Si la sortie du prochain item doit être choisie, sinon cela prendre une sortie au hazard parmis la liste des sorties
        self.block_bellow: Block | None= None
        self.update_interval: int = update_each # in miliseconds
        pass
    @property
    def texture(self) -> Surface:
        return self._texture if type(self._texture) == Surface else get_texture("blocks", self._texture)
    @property
    def coordonates(self) -> tuple[int, int] | None:
        """ Returns the block coordonates
        """
        assert self.game, "Cannot calculate position without the game object"
        found= self.game.map.find_blocks(lambda block: block == self)
        if not len(found) == 1: return None
        return found[0][0]
    def draw(self):
        """ Tries to draw the block and returns if False if the block has not been drawed, else returns True
        """
        assert self.game, "Cannot draw block without the game object"
        x, y= self.game.cam.get_screen_position(self.coordonates)
        width, height= display.get_window_size()
        if not (
            -self.game.cam.zoom <= x <= width
            and -self.game.cam.zoom <= y <= height
        ): return False

        angle= -self.right_rotations * 90
        texture= transform.scale(
            transform.rotate(
                self.texture, 
                angle
            ), [self.game.cam.zoom]*2
        )
        self.game.pygame.screen.blit(self.postprocessing(texture), (x, y))
        return True
    def exec(self): pass
    def edit(self) -> bool: pass
    def fast_edit(self) -> bool: pass
    def postprocessing(self, texture: Surface) -> Surface: return texture
    def __str__(self) -> str:
        return self.identifier[0].upper()

class Seller(Block):
    def __init__(self, game, sell_type: list[Item]= []) -> None:
        super().__init__(game, identifier= "seller", inputs= Direction.fast("a"), texture= "seller", max_level= 1, rotable= False)
        self.accept= sell_type
    def exec(self):
        if self.requires_maintenance or not self.processing_items: return

        item = self.processing_items[0] # Pas de pop() car si l'item est invalide on le laisse dans la machine
        if not self.accept or item in self.accept:
            self.processing_items.pop(0)
            self.game.player.selled.append(item)
            
            item_value= item.value * self.game.marked.get_court(item)
            self.game.player.gain(item_value)
            self.game.marked.selled(item)
        else:
            self.requires_maintenance= True
class GlobalSeller(Seller):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.identifier= "global_seller"
        self._texture= "global_seller"
        pass

class Trash(Block):
    def __init__(self, game) -> None:
        super().__init__(game, identifier= "trash", texture= "trash",  inputs= Direction.fast("a"), rotable= False)
    def exec(self):
        self.processing_items= []

class Generator(Block):
    def __init__(self, game, ingot_type: type[Item]= Stone, ingot_spawn_chance: float = .35) -> None:
        assert 0 <= ingot_spawn_chance <= 1, "Spawn change must be between 0 and 1 included"
        super().__init__(game, "generator", outputs= Direction.fast("a"), texture= "generator", rotable= False)

        self.others: list[type[Item]]= [Stone]
        self.spawn_chance= ingot_spawn_chance
        self.change_extractor(ingot_type)
    def exec(self):
        if len(self.processed_items) > 2: return
        self.processed_items.append(
            (self.extracts if random() <= self.spawn_chance else choice(self.others)) # Ici on séléctionne la classe adécquate
            (self.game) # Et ici on instancie cette classe
        )
    def change_extractor(self, ingot_type: type[Item]):
        self.ingot_texture= ingot_type(self.game).texture
        self.extracts = ingot_type
    def postprocessing(self, texture: Surface) -> Surface:
        ingot_texture= self.ingot_texture
        texture_size= texture.get_size()[0]
        ingot_texture_size= texture_size /2
        
        ingot_texture_pos= (texture_size - ingot_texture_size) /2
        texture.blit(
            transform.scale(ingot_texture, [ingot_texture_size] *2),
            [ingot_texture_pos] *2
        )
        return texture

class DiamondGenerator(Generator):
    def __init__(self, game) -> None:
        from items import DiamondIngot
        super().__init__(game, ingot_type= DiamondIngot, ingot_spawn_chance=.25)
    
class GoldGenerator(Generator):
    def __init__(self, game) -> None:
        from items import GoldIngot
        super().__init__(game, ingot_type= GoldIngot)

class IronGenerator(Generator):
    def __init__(self, game) -> None:
        from items import IronIngot
        super().__init__(game, ingot_type= IronIngot)

class Sorter(Block):
    def __init__(self, game, valid_items: list[Item]= []) -> None:
        super().__init__(game, "sorter", inputs= Direction.fast("n"), outputs= Direction.fast("se"), texture= "sorter", max_level= 5)
        self.valid= valid_items
    def exec(self):
        if not self.processing_items or self.processed_items: return

        item = self.processing_items.pop(0)
        is_valid_item= not bool(self.valid) # = If the valid list is empty, the given item is set as valid
        for element in self.valid:
            if isinstance(item, element.__class__):
                is_valid_item= True
                break
        if is_valid_item:
            self.next_item_output = Direction.fast("s")
        else:
            self.next_item_output = Direction.fast("e")
        self.processed_items.append(item)
    def edit(self) -> bool:
        from items import GoldIngot, Stone, DiamondIngot, IronIngot
        valid_items = [
            Instance(self.game)
            for Instance in (GoldIngot, Stone, DiamondIngot, IronIngot)
        ]
        selector= Selector(self.game, valid_items, freeze_game= True)
        item= selector.get()
        if isinstance(item, Item):
            self.valid= [item]
        return False

class Convoyer(Block):
    def __init__(self, game) -> None:
        super().__init__(game, identifier="convoyer_belt", inputs=Direction.fast("n"), outputs= Direction.fast("s"), texture= "covoyer/straigth")
        self.turned: int | False= False
    def set_turned(self, turn_direction: Direction.single):
        assert turn_direction in Direction.fast("h")
        self.turned= turn_direction
        self.outputs= Direction.listify(turn_direction)
        self._texture= f"covoyer/turn_{'right' if turn_direction == Direction.East else 'left'}"
    def set_straight(self):
        self.turned= False
        self.outputs= Direction.fast("s")
        self._texture= "covoyer/straigth"
    def fast_edit(self):
        if not self.turned: self.set_turned(Direction.West)
        elif self.turned == Direction.West: self.set_turned(Direction.East)
        else: self.set_straight()
        return False
    def exec(self):
        if not self.processing_items: return
        self.processed_items.append(self.processing_items.pop(0))

class Viewer(Block):
    def __init__(self, game) -> None:
        super().__init__(game, "viewer", inputs= Direction.fast("n"), outputs = Direction.fast("s"), decorative= True)
    def exec(self):
        if not self.processing_items: return
        self.processed_items.append(self.processing_items.pop(0))
    def postprocessing(self, texture: Surface) -> Surface:
        if not self.processing_items: return texture

        ingot_texture= self.processing_items[0].texture
        texture_size= texture.get_size()[0]
        ingot_texture_size= texture_size /2
        
        ingot_texture_pos= (texture_size - ingot_texture_size) /2
        texture.blit(
            transform.scale(ingot_texture, [ingot_texture_size] *2),
            [ingot_texture_pos] *2
        )
        return texture

class FloorBlock(Block):
    def __init__(self, game, identifier: str, texture="default_floor_texture") -> None:
        super().__init__(game, identifier= identifier, texture= texture, decorative= True, rotable= False)

class EmptyBlock(FloorBlock):
    def __init__(self, game) -> None:
        super().__init__(game, identifier="empty", texture="empty")
        pass
class MineBlock(FloorBlock):
    def __init__(self, game, mine_type: type[Item]) -> None:
        super().__init__(game, "mine", "mine")
        self.ressource= mine_type
    def postprocessing(self, texture: Surface) -> Surface:
        ressource_texture= self.ressource(self.game).texture
        texture_size= texture.get_size()[0]
        ressource_texture_size= texture_size /2
        
        ingot_texture_pos= (texture_size - ressource_texture_size) /2
        texture.blit(
            transform.scale(ressource_texture, [ressource_texture_size] *2),
            [ingot_texture_pos] *2
        )
        return texture

if __name__ == "__main__":
    t=Trash(None)
    s=Sorter(None)
    pass