from uuid import uuid1

class Item:
    def __init__(self, game, name: str, value: float, texture= "default_item_texture") -> None:
        from blocks import Block
        self.id= uuid1()
        self.name= name
        self.value= value
        self.texture= texture
        self.crafts: list[dict[dict[str["block"], Block], dict[str["items"], list[Item]]]] = []
        pass

class GoldIngot(Item):
    def __init__(self, game):
        from blocks import GoldGenerator
        super().__init__(game, "gold_ingot", 10, "gold_ingot")
        self.crafts= [
            {"block": GoldGenerator}
        ]
    
