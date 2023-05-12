from direction_sys import Direction

class Block:
    def __init__(self, game, type: str, inputs: Direction.typeof= Direction.fast("x"), outputs: Direction.typeof= Direction.fast("x"), texture= "default_block_texture", decorative=False, default_level= 1, max_level= 20) -> None:
        from items import Item

        self.game= game
        self.type= type
        self.input= inputs
        self.output= outputs
        self.locked= False
        self.connected: dict[str, list[Block]]= {
            "in": [],
            "out": []
        }
        self.position: tuple[int, int]= None
        self.deletable= not decorative
        self.interactable= not decorative
        self.requires_update= not decorative
        self.texture= texture
        self.level= {
            "now": default_level,
            "max": default_level if decorative else max_level
        }
        self.processing_items: list[Item] = []
        self.processed_items: list[Item] = []
        pass
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
        super().__init__(game, "global_seller", Direction.fast(), texture= "global_seller", max_level= 1)
        pass
    def exec(self):
        item= self.processing_items.pop(0)
        self.game.player.sell(item)
    

class Trash(Block):
    def __init__(self, game) -> None:
        super().__init__(game, "trash", Direction.fast())
    def exec(self):
        self.processing_items= []

class GoldGenerator(Block):
    def __init__(self, game) -> None:
        super().__init__(game, "generator", outputs= Direction.fast(), texture= "gold_generator")
    def exec(self):
        from items import GoldIngot
        self.processed_items.append(GoldIngot(self.game))

if __name__ == "__main__":
    pass