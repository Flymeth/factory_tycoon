from blocks import Block, EmptyBlock, Trash
from direction_sys import Direction

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

        self.game= game
        self.zoom= zoom
        self.matrice= init
        self.center= (self.width//2, self.height//2) # Les coordonnées du centre du monde
        pass

    @staticmethod
    def create_coordonates(x = int, y = int):
        return x, y
    def get_block(self, x = int, y = int):
        return self.matrice[x][y]

    @property
    def width(self):
        return len(self.matrice or [])
    @property
    def height(self):
        return len(self.matrice[0]) if self.width else 0
    @property
    def create_coordonates(self):
        return Map.create_coordonates

    def generate_chuck(self, width: int, height: int) -> list[list[Block]]:
        """ Creates on random chuck and returns it
        """
        return [[EmptyBlock(self.game) for y in range(height)] for x in range(width)]
    def create_chunks(self, direction: Direction.typeof= Direction.fast(), size= 20) -> tuple[list[list[Block]]]:
        """ Creates chunks in different directions and add them directly to the map
            Returns a tuple containing the created chunks in order of the given directions orders
        """

        generated= []
        for dir in Direction.listify(direction):
            if dir == Direction.North or dir == Direction.South:
                chunck= self.generate_chuck(self.width, size)
                
                for index, column in enumerate(self.matrice):
                    if index > self.width:
                        self.create_chunks(Direction.East, 1)
                    if dir == Direction.North:
                        self.center = ( # As we modify all the map's block position, we need to modify the map's center
                            self.center[0], 
                            self.center[1] + size
                        )
                        self.matrice[index] = chunck[index] + column
                    else:
                        self.matrice[index] += chunck[index]
            elif dir == Direction.East or dir == Direction.West:
                chunck= self.generate_chuck(size, self.height)

                if dir == Direction.East:
                    self.matrice += chunck
                else:
                    self.center = ( # As we modify all the map's block position, we need to modify the map's center
                        self.center[0] + size, 
                        self.center[1]
                    )
                    self.matrice = chunck + self.matrice
            else: raise AssertionError(f"Invalid chunk direction (received '{dir}')")

            generated.append(chunck)
        return tuple(generated)
    
    def __str__(self) -> str:
        reversed_map: list[list[Block]]= []
        for column in self.matrice:
            for index, block in enumerate(column):
                if index >= len(reversed_map):
                    reversed_map.append([])
                reversed_map[index].append(str(block))
        str_map = "\n".join(["".join(column) for column in reversed_map])
        return str_map

if __name__ == "__main__":
    m= Map(None, init= [[Trash(None)]])
    print(m.center)
    m.create_chunks(Direction.fast("a"))
    print(m)
    print(m.center)
    print(m.get_block(*m.center))