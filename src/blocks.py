from direction_sys import Direction
from items import *
from random import random, choice
from textures import get_texture
from pygame import transform, display, Surface, Rect
from gui.selector import Selector
from typing import Self, Literal, Type

class Block:
    def __init__(self, game, identifier: str, inputs: Direction.multiple= Direction.fast(), outputs: Direction.multiple= Direction.fast(), texture: str | Surface= "", decorative=False, default_level= 1, max_level= 20, right_rotations: int = 0, rotable: bool= True, update_each: int= 1000, max_storage_item= 1) -> None:
        from items import Item
        from _main import Game

        self.game: Game= game
        self.identifier= identifier
        self.inputs= inputs
        self.outputs= outputs
        self.locked= False
        self.connected: dict[Literal["out", "in"], list[tuple[int, Block]]]= {
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
        self._cache_coordonates: tuple[int, int] | None= None
        self.max_storage= max_storage_item
        pass
    @property
    def texture(self) -> Surface:
        return self._texture if type(self._texture) == Surface else get_texture("blocks", self._texture)
    @property
    def coordonates(self) -> tuple[int, int] | None:
        """ Returns the block coordonates
        """
        assert self.game, "Cannot calculate position without the game object"
        if self._cache_coordonates: return self._cache_coordonates
        found= self.game.map.find_block(lambda block: block == self)
        if not found: return None
        coordonates= found[0]
        self._cache_coordonates= coordonates
        return coordonates
    def get_rect(self) -> Rect | None:
        if not self.coordonates: return
        x, y= self.game.cam.get_screen_position(self.coordonates)
        width, height= display.get_window_size()
        if(
            -self.game.cam.zoom <= x <= width
            and -self.game.cam.zoom <= y <= height
        ): return Rect(x, y, self.game.cam.zoom, self.game.cam.zoom)
    def get_surface(self) -> Surface:
        angle= -self.right_rotations * 90
        return transform.rotate(
            self.texture, 
            angle
        )
    def draw(self) -> bool:
        """ Tries to draw the block and returns False if the block has not been drawed, else returns True
        """
        rect = self.get_rect()
        if not rect: return False

        texture= transform.scale(self.get_surface(), rect.size)
        self.game.draw(self.postprocessing(texture), rect.topleft)
        return True
    def exec(self): pass
    def edit(self) -> bool: pass
    def fast_edit(self) -> bool: pass
    def postprocessing(self, texture: Surface) -> Surface: return texture
    def item_predicate(self, item: Item) -> bool: return True
    def duplicate(self) -> Self:
        new_block = self.__class__(self.game)
        new_block.right_rotations= self.right_rotations
        return new_block
    def __str__(self) -> str:
        return self.identifier[0].upper()

class Seller(Block):
    def __init__(self, game, sell_type: list[Item]= []) -> None:
        super().__init__(game, identifier= "seller", inputs= Direction.fast("a"), texture= "seller", max_level= 1, rotable= False, update_each= 200, max_storage_item= float("inf"))
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
        super().__init__(game, identifier= "trash", texture= "trash",  inputs= Direction.fast("a"), rotable= False, update_each= 1, max_storage_item= float("inf"))
    def exec(self):
        if self.processing_items:
            self.processing_items= []

class Generator(Block):
    def __init__(self, game, ingot_type: type[Item]= Stone, ingot_spawn_chance: float = .35) -> None:
        assert 0 <= ingot_spawn_chance <= 1, "Spawn change must be between 0 and 1 included"
        super().__init__(game, "generator", outputs= Direction.fast("a"), texture= "generator", rotable= False, update_each= 2000)

        self.others: list[type[Item]]= [Stone]
        self.spawn_chance= ingot_spawn_chance
        self.change_extractor(ingot_type)
    def exec(self):
        if not self.connected["out"]: return
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
        ingot_texture_size= texture_size /3
        
        ingot_texture_pos= texture_size - ingot_texture_size * 1.02
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
        super().__init__(game, "sorter", inputs= Direction.fast("n"), outputs= Direction.fast("se"), texture= "sorter", max_level= 5, max_storage_item= 4)
        self.valid= valid_items
        self.inverted= False
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
            self.next_item_output = Direction.fast("w" if self.inverted else "e")
        self.processed_items.append(item)
    def fast_edit(self) -> bool:
        self.inverted= not self.inverted
        if self.inverted:
            self.outputs= Direction.fast("sw")
        else:
            self.outputs= Direction.fast("se")
        return True
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
    def postprocessing(self, texture: Surface) -> Surface:
        if self.inverted:
            rotate_x= self.right_rotations%2 == 0
            texture= transform.flip(texture, rotate_x, not rotate_x)
        return texture

class Convoyer(Block):
    def __init__(self, game) -> None:
        super().__init__(game, identifier="convoyer_belt", inputs=Direction.fast("s"), outputs= Direction.fast("n"), texture= "covoyer/straigth", max_storage_item= 3)
        self.turned: int | Literal[False]= False
        self.__anim_items: list[tuple[Item, float]]= [] # (item, animation_state)[]
    def set_turned(self, turn_direction: Direction.single):
        assert turn_direction in Direction.fast("h"), "Invalid turn direction has been set"
        self.turned= turn_direction
        self.outputs= Direction.listify(turn_direction)
        self._texture= f"covoyer/turn_{'right' if turn_direction == Direction.East else 'left'}"
    def set_straight(self):
        self.turned= False
        self.outputs= Direction.fast("n")
        self._texture= "covoyer/straigth"
    def fast_edit(self):
        if not self.turned: self.set_turned(Direction.East)
        elif self.turned == Direction.East: self.set_turned(Direction.West)
        else: self.set_straight()
        return True
    def exec(self):
        if not self.processing_items or len(self.processed_items) >= self.max_storage: return
        self.processed_items.append(self.processing_items.pop(0))
    def postprocessing(self, texture: Surface) -> Surface:
        if not (self.processed_items + self.processing_items): return texture
        require_drawing= (self.processed_items + self.processing_items)[:self.max_storage]
        texture_size = texture.get_size()[0]
        item_size = texture_size /2.5

        animation_state: float = (self.game.time_infos.time["ms"]%self.update_interval) / self.update_interval # 0 <= x <= 1
        animation_start_dir = Direction.rotate(self.inputs[0], self.right_rotations)
        animation_end_dir   = Direction.rotate(self.outputs[0], self.right_rotations)

        valid_positions: dict[int, tuple[float, float]]= {
            Direction.North: ((texture_size - item_size)/2, -item_size /2),
            Direction.South: ((texture_size - item_size)/2, texture_size - item_size/2),
            Direction.West: (-item_size /2, (texture_size - item_size)/2),
            Direction.East: (texture_size - item_size/2, (texture_size - item_size)/2)
        }

        animation_start_position= valid_positions.get(animation_start_dir)
        animation_end_position  = valid_positions.get(animation_end_dir)

        # remove unfounded items
        for element in self.__anim_items:
            item, anim_state= element
            if not item in require_drawing:
                self.__anim_items.remove(element)
        # Adds new items
        for item in require_drawing:
            if not next((1 for i, anim_state in self.__anim_items if i == item), None):
                self.__anim_items.append([item, 0])
        
        # Draw all items
        for index, element in enumerate(self.__anim_items):
            item, anim_state= element
            item_texture= transform.scale(item.texture, [item_size] *2)

            item_position= 0, 0
            if self.turned:
                STRENGHT = 2
                states= (
                    anim_state** STRENGHT,
                    1- (1 - anim_state)** STRENGHT
                )
                if animation_end_dir in (Direction.North, Direction.South):
                    states = states[1], states[0]
                item_position = [
                    animation_start_position[i] + (animation_end_position[i] - animation_start_position[i]) * states[i]
                    for i in range(2)
                ]
            else:
                item_position = [
                    animation_start_position[i] + (animation_end_position[i] - animation_start_position[i]) * anim_state
                    for i in range(2)
                ]
            
            new_anim_state= (animation_state / self.max_storage) * (self.max_storage - index)
            if anim_state < .995 and new_anim_state > anim_state:
                self.__anim_items[index][1]= new_anim_state
            texture.blit(item_texture, item_position)
        return texture
    def duplicate(self) -> Self:
        new_block= super().duplicate()
        new_block.set_straight()
        if self.turned:
            new_block.right_rotations+= self.turned
            new_block.right_rotations%= 4
        return new_block

class Connecter(Block):
    def __init__(self, game) -> None:
        super().__init__(game, identifier= "connecter", inputs= Direction.fast("h"), outputs= Direction.fast("s"), texture= "connecter", update_each= 100, max_storage_item= 2)
    def exec(self):
        self.processed_items+= [*self.processing_items]
        self.processing_items= []

class Smelter(Block):
    def __init__(self, game) -> None:
        super().__init__(game, "smelter", Direction.fast("a"), Direction.fast("a"), texture= "smelter", rotable= False, update_each= 2000, max_storage_item= 2)
    def exec(self):
        if not self.processing_items: return
        item= self.processing_items.pop()
        item.temperature= 1
        self.processed_items.append(item)

class Press(Block):
    def __init__(self, game) -> None:
        super().__init__(game, "press", inputs= Direction.fast("n"), outputs= Direction.fast("s"), texture= "press", update_each= 1000, max_storage_item= 2)
        self.transforms: dict[Item: Item] = {
            IronIngot: IronPlate,
            GoldIngot: GoldPlate
        }
    def item_predicate(self, item: Item) -> bool:
        return item.temperature >= .5 and type(item) in self.transforms
    def exec(self):
        if not self.processing_items: return
        item= self.processing_items.pop(0)
        new_item: Item = self.transforms[type(item)](self.game)
        new_item.temperature= item.temperature
        self.processed_items.append(new_item)

class Stroker(Block):
    def __init__(self, game) -> None:
        super().__init__(game, "stroker", inputs=Direction.fast("n"), outputs= Direction.fast("s"), texture= "stroker", max_storage_item= 3)
        self.transforms: dict[Type[Item], Type[Item]] = {
            IronIngot: IronString,
            GoldIngot: GoldString,
            DiamondIngot: DiamondString
        }
    def exec(self):
        if len(self.processing_items) < 3: return
        items = self.processing_items[:3]
        if not [1 for item in items[1:] if item.name == items[0].name]: return
        element = type(items[0])
        if not element in self.transforms: return
        self.processed_items.append(self.transforms[element](self.game))
        for i in range(3): self.processing_items.pop()

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
        
        ingot_texture_pos= (texture_size - ressource_texture_size) /2, texture_size - ressource_texture_size * 1.05
        texture.blit(
            transform.scale(ressource_texture, [ressource_texture_size] *2),
            ingot_texture_pos
        )
        return texture

if __name__ == "__main__":
    t=Trash(None)
    s=Sorter(None)
    pass