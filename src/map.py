from blocks import Block, FloorBlock, EmptyBlock, Trash, MineBlock, Generator
from direction_sys import Direction
from pygame.display import get_window_size
from typing import Callable

class Map:
    def __init__(self, game, init: list[list[Block]]= [], auto_generate_chunks= True) -> None:
        from _main import Game

        self.game: Game= game
        self.matrice= init
        self.__center= (self.width//2, self.height//2) # Les coordonnées du centre du monde
        if auto_generate_chunks:
            self.game.add_event("tick", lambda g, e: self.check_and_generate_chunks())
        pass
    def check_and_generate_chunks(self):
        extremities= {
            "tl": self.matrice[0][0],
            "tr": self.matrice[-1][0],
            "bl": self.matrice[0][-1],
            "br": self.matrice[-1][-1]
        }
        generate_direction= Direction.fast("x")
        width, height= get_window_size()
        for key in extremities:
            x, y= self.game.cam.get_screen_position(extremities[key].coordonates)
            if "t" in key and y > -self.game.cam.zoom:
                generate_direction+= Direction.fast("n")
            if "b" in key and y < height:
                generate_direction+= Direction.fast("s")
            if "l" in key and x > -self.game.cam.zoom:
                generate_direction+= Direction.fast("w")
            if "r" in key and x < width:
                generate_direction+= Direction.fast("e")
        generate_direction= list(set(generate_direction))
        self.generate_chunks(generate_direction, 1)
        pass

    @staticmethod
    def create_coordonates(x: int, y: int):
        return x, y
    def __generic_coordonates_to_matrice_coordonate__(self, x: int, y: int):
        """ [PRIVATE METHOD]-> Transform coordonates to the map's matrice corresponding block index in x and y
                Note:
                    Generic coordonates corespond as the coordonates as:
                        (0, 0) corresponds to the map's center
                    > See [README.md]
        """
        return self.__center[0] - x, self.__center[1] - y
    def __matrice_coordonates_to_generic_coordonate__(self, x: int, y: int):
        """ [PRIVATE METHOD]-> Transform matrice block index in x and y to coorsponding coordonates on the map
                Note:
                    Matrice coordonates corespond as the coordonates as:
                        (0, 0) corresponds to the map's top left
                    > See [README.md]
        """
        return x - self.__center[0], y - self.__center[1]
    @property
    def width(self):
        return len(self.matrice or [])
    @property
    def height(self):
        return len(self.matrice[0]) if self.width else 0
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
            if dir in (Direction.North, Direction.South):
                chunck= self.create_chuck(self.width, size)

                for index in range(self.width):
                    if dir == Direction.North:
                        self.__center = ( # As we modify all the map's block position, we need to modify the map's center
                            self.__center[0], 
                            self.__center[1] + size
                        )
                        self.matrice[index] = chunck[index] + self.matrice[index]
                    else:
                        self.matrice[index] += chunck[index]
            elif dir in (Direction.East, Direction.West):
                chunck= self.create_chuck(size, self.height)

                if dir == Direction.East:
                    self.matrice += chunck
                else:
                    self.__center = ( # As we modify all the map's block position, we need to modify the map's center
                        self.__center[0] + size, 
                        self.__center[1]
                    )
                    self.matrice = chunck + self.matrice
            else: raise AssertionError(f"Invalid chunk direction (received '{dir}')")

            generated.append(chunck)
        return tuple(generated)
    
    def place(self, block: Block, coordonates: tuple[int, int]):
        """ Places a block in the map
            This method crashes if there is another block at this position

            Note:
                coordonates -> The generic coordonates
        """
        x, y= self.__generic_coordonates_to_matrice_coordonate__(*coordonates)
        assert 0 <= x < self.width and 0 <= y < self.height, "The map has not been generated here (cannot place the block)"

        actual_block= self.matrice[x][y]
        assert isinstance(actual_block, FloorBlock), "Tried to place a block above another"
        if isinstance(actual_block, MineBlock) and isinstance(block, Generator):
            assert isinstance(block.extracts, type(actual_block.ressource)), "Tried to place a generator on an invalid mine"
        block.block_bellow= actual_block
        self.matrice[x][y]= block

        # Connect block with sided ones #
        for overflow_x in range(-1, 2):
            for overflow_y in range(-1, 2):
                if bool(overflow_x) == bool(overflow_y): continue # On ne check ni la diagonale, ni le block en question
                x, y= coordonates[0] + overflow_x, coordonates[1] + overflow_y
                if 0 <= x <= self.width and 0 <= y <= self.height:
                    side_block= self.matrice[x][y]
                    if isinstance(side_block, FloorBlock): continue

                    # Sided_block connection side (without any rotation)
                    initial_sided_possible_connection= \
                        Direction.North if overflow_y == 1 else \
                        Direction.South if overflow_y == -1 else \
                        Direction.East if overflow_x == -1 else Direction.West
                    # Same with rotation
                    rotated_sided_possible_connection= Direction.rotate(initial_sided_possible_connection, side_block.right_rotations)
                    if not (
                        initial_sided_possible_connection in side_block.inputs + side_block.outputs
                    ): continue

                    # Block connection side (without any rotation)
                    initial_block_possible_connection= (initial_sided_possible_connection +2) %4
                    # Same with rotation
                    rotated_block_possible_connection= Direction.rotate(initial_block_possible_connection, block.right_rotations)
                    if not (
                        initial_block_possible_connection in block.inputs + block.outputs
                    ): continue

                    expected_rotated_sided_connection= (rotated_block_possible_connection +2) %4
                    if (expected_rotated_sided_connection == rotated_sided_possible_connection
                        and ((
                            initial_sided_possible_connection in side_block.inputs
                            and initial_block_possible_connection in block.outputs
                        )or (
                            initial_sided_possible_connection in side_block.outputs
                            and initial_block_possible_connection in block.inputs
                        )
                    )):
                        receiver, sender = (
                            (block, side_block) 
                            if initial_block_possible_connection in block.inputs
                            else (side_block, block)
                        )
                        receiver_connection, sender_connection= (
                            (initial_block_possible_connection, initial_sided_possible_connection)
                            if receiver == block
                            else (initial_sided_possible_connection, initial_block_possible_connection)
                        )

                        # Get input/output connection index
                        receiver_input_index= receiver.inputs.index(receiver_connection)
                        sender_output_index = sender.outputs.index(sender_connection)

                        # Connect both blocks
                        receiver.connected["in"]= [
                            connection for connection in receiver.connected["in"]
                            if connection[0] != receiver_input_index
                        ] + [(receiver_input_index, sender)]
                        sender.connected["out"]= [
                            connection for connection in sender.connected["out"]
                            if connection[0] != sender_output_index
                        ] + [(sender_output_index, receiver)]
        # ----------------------------------------------------------------------------- #
    def delete(self, coordonates: tuple[int, int]) -> Block:
        """ Deletes a block in the map and returns it
            This method crashes if there isn't any block at this position
        """
        coordonates= self.__generic_coordonates_to_matrice_coordonate__(*coordonates)
        assert not isinstance(self.matrice[coordonates[0]][coordonates[1]], FloorBlock), "Tried to delete the floor"
        x, y= coordonates
        deleted = self.matrice[x][y]
        # Remove connections
        for connection_in, block in deleted.connected["in"]:
            if block == deleted:
                connection_out= (connection_in+2) %4
                block.connected["out"].remove((connection_out, deleted))
        for connection_out, block in deleted.connected["out"]:
            if block == deleted:
                connection_in= (connection_in+2) %4
                block.connected["in"].remove((connection_in, deleted))
        # --------------------------------------------------------------
        assert deleted.block_bellow, "Error: cannot replace the block because it doesn't have a bellow_block in stockage" # Normalement ce assert ne sert à rien, mais ne pas l'enlever
        self.matrice[x][y]= deleted.block_bellow
        return deleted
    def get_block(self, x: int, y: int) -> Block:
        x, y= self.__generic_coordonates_to_matrice_coordonate__(x, y)
        return self.matrice[x][y]
    def find_blocks(self, predicate: Callable[[Block], bool]= lambda block:False) -> list[tuple[tuple[int, int], Block]]:
        return [
            (self.__matrice_coordonates_to_generic_coordonate__(x, y), self.matrice[x][y])
            for x in range(len(self.matrice))
            for y in range(len(self.matrice[x]))
            if predicate(self.matrice[x][y])
        ]

    def flatten(self) -> list[Block]:
        return [self.matrice[x][y] for x in range(self.width) for y in range(self.height)]
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
    m.generate_chunks(Direction.fast("es"), 5)
    print(m)

    # my_trash= Trash(None)
    # my_sorter= Sorter(None)
    # m.place(my_trash, Map.create_coordonates(5, 5))
    # m.place(my_sorter, Map.create_coordonates(5, 4))
    pass