from blocks import Block, FloorBlock, EmptyBlock, Trash, MineBlock, Generator, GoldGenerator
from direction_sys import Direction
from typing import Callable

class Map:
    def __init__(self, game, zoom= 15, init: list[list[Block]]= []) -> None:
        """
            Note:
                Zoom
                Le zoom correspond au nombre de blocks que le joueur peut voir sur une ligne de large
                    Ex:
                    zoom = 3
                    3 blocks prendront la totalité de la largeur de l'écran
        """
        from _main import Game

        self.game: Game= game
        self.zoom= zoom
        self.matrice= init
        self.floor= self.create_chuck(self.width, self.height)
        self.center= (self.width//2, self.height//2) # Les coordonnées du centre du monde
        pass

    @staticmethod
    def create_coordonates(x = int, y = int):
        return x, y
    @property
    def width(self):
        return len(self.matrice or [])
    @property
    def height(self):
        return len(self.matrice[0]) if self.width else 0
    @property
    def create_coordonates(self):
        return Map.create_coordonates
    def create_chuck(self, width: int, height: int) -> list[list[Block]]:
        """ Creates on random chuck and returns it
        """
        return [[EmptyBlock(self.game) for y in range(height)] for x in range(width)]
    def generate_chunks(self, direction: Direction.typeof= Direction.fast(), size= 20) -> tuple[list[list[Block]]]:
        """ Creates chunks in different directions and add them directly to the map
            Returns a tuple containing the created chunks in order of the given directions orders
        """

        generated= []
        for dir in Direction.listify(direction):
            if dir == Direction.North or dir == Direction.South:
                chunck= self.create_chuck(self.width, size)
                for index, column in enumerate(self.matrice):
                    if index > self.width:
                        self.generate_chunks(Direction.East, 1)
                    if dir == Direction.North:
                        self.matrice[index] = chunck[index] + column
                        self.floor[index] = chunck[index] + self.floor[index]
                    else:
                        self.matrice[index] += chunck[index]
                        self.floor[index]+= chunck[index]
                
                self.center = ( # As we modify all the map's block position, we need to modify the map's center
                    self.center[0], 
                    self.center[1] + size
                )
            elif dir == Direction.East or dir == Direction.West:
                chunck= self.create_chuck(size, self.height)

                if dir == Direction.East:
                    self.matrice += chunck
                    self.floor+= chunck
                else:
                    self.center = ( # As we modify all the map's block position, we need to modify the map's center
                        self.center[0] + size, 
                        self.center[1]
                    )
                    self.matrice = chunck + self.matrice
                    self.floor= chunck + self.floor
            else: raise AssertionError(f"Invalid chunk direction (received '{dir}')")

            generated.append(chunck)
        return tuple(generated)
    
    def place(self, block: Block, coordonates: tuple[int, int]):
        """ Places a block in the map
            This method crashes if there is another block at this position
        """
        actual_block= self.get_block(*coordonates)
        assert isinstance(actual_block, FloorBlock), "Tried to place a block above another"
        # for overflow_x in range(-1, 2):
        #     for overflow_y in range(-1, 2):
        #         if overflow_x == overflow_y == 0: continue
        #         x, y= coordonates[0] + overflow_x, coordonates[1] + overflow_y
        #         if 0 <= x <= self.width and 0 <= y <= self.height:
        #             self.matrice[x][y].connected
        # ^^^^^^^ Not finished
        if isinstance(actual_block, MineBlock) and isinstance(block, Generator):
            assert isinstance(block.extracts, type(actual_block.ressource)), "Tried to place a generator on an invalid mine"
        self.matrice[coordonates[0]][coordonates[1]]= block
    def delete(self, coordonates: tuple[int, int]) -> Block:
        """ Deletes a block in the map and returns it
            This method crashes if there isn't any block at this position
        """
        assert not isinstance(self.get_block(*coordonates), FloorBlock), "Tried to delete the floor"
        x, y= coordonates
        deleted = self.matrice[x][y]
        self.matrice[x][y]= self.floor[x][y]
        return deleted
    def get_block(self, x = int, y = int) -> Block:
        return self.matrice[x][y]
    def find_blocks(self, predicate: Callable[[Block], bool]= lambda block:False) -> list[tuple[tuple[int, int], Block]]:
        return [
            ((x, y), self.get_block(x, y))
            for x in range(len(self.matrice))
            for y in range(len(self.matrice[x]))
            if predicate(self.matrice[x][y])
        ]

    def __str__(self) -> str:
        reversed_map: list[list[Block]]= []
        for column in self.matrice:
            for index, block in enumerate(column):
                if index >= len(reversed_map):
                    reversed_map.append([])
                reversed_map[index].append(str(block))
        str_map = "\n".join(["".join(column) for column in reversed_map])
        return str_map
    def __len__(self) -> int:
        return len(self.matrice) * len(self.matrice[0])

if __name__ == "__main__":
    from items import GoldIngot

    m= Map(None, init= [[Trash(None)]])
    print(m.center)
    m.generate_chunks(Direction.fast("wn"))
    print(m)
    print(m.center)
    print(m.get_block(*m.center))
    print(type(MineBlock(None, GoldIngot(None)).ressource), type(GoldGenerator(None).extracts))
    print(isinstance(MineBlock(None, GoldIngot(None)).ressource, type(GoldGenerator(None).extracts)))