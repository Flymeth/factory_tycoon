from blocks import Block, EmptyBlock
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
                --------------------------------------------------------------------------------------
                Type de la matrice
                coordonnée en 'x', puis en 'y'
                    Ex:
                            (x, 0)(x, 1)(x, 2)(x, 3)(x, 4)(x, 5)
                            _____________________________________
                    (0, y)  |     |     |     |     |     |     |
                            |-----|-----|-----|-----|-----|-----|
                    (1, y)  |     |     |     |     |     |     |
                            |-----|-----|-----|-----|-----|-----|
                    (2, y)  |     |     |     |     |     |     |
                            |-----|-----|-----|-----|-----|-----|
                    (3, y)  |     |     |     |     |     |     |
                            |-----|-----|-----|-----|-----|-----|
                    (4, y)  |_____|_____|_____|_____|_____|_____|
        """

        self.game= game
        self.zoom= zoom
        self.matrice= init
        self.center= (self.width//2, self.height//2) # Les coordonnées du centre du monde
        pass

    @property
    def width(self):
        return len(self.matrice[0]) if self.height else 0
    @property
    def height(self):
        return len(self.matrice or [])

    def generate_chuck(self, width: int, height: int) -> list[list[Block]]:
        """ Creates on random chuck and returns it
        """
        return [[EmptyBlock(self.game) for y in range(height)] for x in range(width)]
    def create_chunks(self, direction: Direction.typeof= Direction.fast(), size= 20) -> tuple[list[list[Block]]]:
        """ Creates chunks in different directions and add them directly to the map
            Returns a tuple containing the created chunks in order of the given directions orders
        """

        generated= []
        for dir in Direction.unconstruct(direction):
            if dir == "north" or dir == "south":
                chunck= self.generate_chuck(self.width, size)
                for index, column in enumerate(self.matrice):
                    if dir == "north":
                        self.matrice[index] = chunck[index] + column
                    else:
                        self.matrice[index] += chunck[index]
            elif dir == "east" or dir == "west":
                chunck= self.generate_chuck(size, self.height)
                if dir == "east":
                    self.matrice += chunck
                else:
                    self.matrice = chunck + self.matrice
            else: raise AssertionError(f"Invalid chunk direction (received '{dir}')")

            generated.append(chunck)
        return tuple(generated)

if __name__ == "__main__":
    m= Map(None)
    m.create_chunks(Direction.fast())
    print(m.matrice)