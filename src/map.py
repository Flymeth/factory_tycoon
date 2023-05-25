from blocks import Block, FloorBlock, EmptyBlock, Trash, MineBlock, Generator
from direction_sys import Direction
from pygame.display import get_window_size
from typing import Callable
from random import choice

class Map:
    def __init__(self, game, init_block: Block, auto_generate_chunks= True) -> None:
        from _main import Game

        self.game: Game= game
        self.matrice= [[init_block]]
        self.__center= 0, 0 # Les coordonnées du centre du monde
        self.ev= self.game.add_event("tick", lambda g, e: self.update())
        if auto_generate_chunks:
            self.game.add_event("tick", lambda g, e: self.check_and_generate_chunks())
        pass
    def update(self):
        """ Update the map's block
        """
        assert self.game, "Game object is required to use this function"
        tick= self.game.pygame.ticks
        if not tick: return

        blocks = self.flatten()
        #! IDK why but the `blocks` array becomes empty when the user is clicking the on screen
        # Updating each blocks (if required)
        [
            block.exec()
            for block in blocks
            if not tick%block.update_interval
        ]
        # Distributing items --> do it after updates to avoid 'fast travel'
        for block in blocks:
            if not tick%block.update_interval:
                if type(block) == Generator:
                    pass
                if block.processed_items and block.outputs and block.connected["out"]:
                    valid_outputs_indexes: list[int]= []
                    if type(block.next_item_output) == Direction.single:
                        if not (block.next_item_output in block.outputs): continue
                        valid_outputs_indexes.append(block.outputs.index(block.next_item_output))
                    else:
                        for direction in block.next_item_output:
                            if not direction in block.outputs: continue
                            valid_outputs_indexes.append(block.outputs.index(direction))
                    if not valid_outputs_indexes: continue
                    
                    valid_blocks= [
                        out_block
                        for index, out_block in block.connected["out"]
                        if index in valid_outputs_indexes
                    ]
                    if not valid_blocks: continue
                    out_block= choice(valid_blocks)
                    out_block.processing_items.append(block.processed_items.pop(0))

    def check_and_generate_chunks(self):
        assert self.game, "Cannot check and generate chunks automatically without the game object"
        extremities= {
            "tl": self.matrice[0][0],
            "tr": self.matrice[-1][0],
            "bl": self.matrice[0][-1],
            "br": self.matrice[-1][-1]
        }
        generate_directions= Direction.fast("x")
        width, height= get_window_size()
        block_size = self.game.cam.zoom
        for key in extremities:
            x, y= self.game.cam.get_screen_position(extremities[key].coordonates)
            
            # Some code samples bellow are not logic, but it works, so fuck it :)
            if "t" in key and y >= 0:
                generate_directions+= Direction.fast("n")
            if "b" in key and y + block_size <= height:
                generate_directions+= Direction.fast("s")
            if "r" in key and x >= 0:
                generate_directions+= Direction.fast("e")
            if "l" in key and x + block_size <= width:
                generate_directions+= Direction.fast("w")
        if generate_directions:
            self.generate_chunks(
                list(set(generate_directions)), # To avoid duplicates
                1 # Number of blocks to generate
            )
            if self.game.DEV_MODE:
                print(f"> AUTOMATICALLY GENERATED TERRAIN (Directions: {generate_directions}).")
    @staticmethod
    def create_coordonates(x: int, y: int):
        assert type(x) == type(y) == int, "Coordonates must be of type `int`"
        return x, y
    def __generic_coordonates_to_matrice_coordonate__(self, x: int, y: int):
        """ [PRIVATE METHOD]-> Transform coordonates to the map's matrice corresponding block index in x and y
                Note:
                    Generic coordonates corespond as the coordonates where:
                        (0, 0) corresponds to the map's center
                    > See [README.md]
        """
        assert type(x) == type(y) == int, "Coordonates must be of type `int`"
        x, y = self.__center[0] - x, self.__center[1] - y
        assert 0 <= x < self.width and 0 <= y < self.height, "Map has not been generated at this coordonates"
        return x, y

    def __matrice_coordonates_to_generic_coordonate__(self, x: int, y: int):
        """ [PRIVATE METHOD]-> Transform matrice block index in x and y to corresponding coordonates on the map
                Note:
                    Matrice coordonates corespond as the coordonates where:
                        (0, 0) corresponds to the top left of the map
                    > See [README.md]
        """
        assert type(x) == type(y) == int, "Coordonates must be of type `int`"
        return self.__center[0] - x, self.__center[1] - y
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

                if dir == Direction.North:
                    self.__center = ( # As we modify all the map's block position, we need to modify the map's center
                        self.__center[0], 
                        self.__center[1] + size
                    )
                for index in range(self.width):
                    if dir == Direction.North:
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
    def actualize(self, coordonates: tuple[int, int]):
        """ Actualize the block for properties that need to be matched with blocks around
        """
        try:
            self.place(self.delete(coordonates), coordonates)
        except AssertionError as err:
            if self.game.DEV_MODE:
                print(f"Cannot actualize block:\n{err}")
    def place(self, block: Block, coordonates: tuple[int, int]):
        """ Places a block in the map
            This method crashes if there is another block at this position

            Note:
                coordonates -> The generic coordonates
        """
        x, y= self.__generic_coordonates_to_matrice_coordonate__(*coordonates)

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
                side_x, side_y= self.__generic_coordonates_to_matrice_coordonate__(coordonates[0] + overflow_x, coordonates[1] + overflow_y)
                if 0 <= side_x <= self.width and 0 <= side_y <= self.height:
                    side_block= self.matrice[side_x][side_y]
                    if isinstance(side_block, FloorBlock): continue

                    # Sided_block connection side (without any rotation)
                    initial_sided_possible_connection= \
                        Direction.North if overflow_y == -1 else \
                        Direction.South if overflow_y == 1 else \
                        Direction.East if overflow_x == -1 else Direction.West
                    # Same with rotation
                    rotated_sided_possible_connection= Direction.rotate(initial_sided_possible_connection, side_block.right_rotations)
                    if not (
                        initial_sided_possible_connection in side_block.inputs + side_block.outputs
                    ): continue

                    # Block connection side (without any rotation)
                    initial_block_possible_connection= (initial_sided_possible_connection +2) %4
                    # Same with rotation
                    rotated_block_possible_connection = Direction.rotate(initial_block_possible_connection, block.right_rotations)
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
        x, y= self.__generic_coordonates_to_matrice_coordonate__(*coordonates)
        assert not isinstance(self.matrice[x][y], FloorBlock), "Tried to delete the floor"
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
    def get_block(self, x: int, y: int) -> Block | None:
        try:
            x, y= self.__generic_coordonates_to_matrice_coordonate__(x, y)
        except AssertionError:
            return None
        return self.matrice[x][y]
    def find_blocks(self, predicate: Callable[[Block], bool]= lambda block:False) -> list[tuple[tuple[int, int], Block]]:
        return [
            (self.__matrice_coordonates_to_generic_coordonate__(x, y), self.matrice[x][y])
            for x in range(len(self.matrice))
            for y in range(len(self.matrice[x]))
            if predicate(self.matrice[x][y])
        ]

    def flatten(self) -> list[Block]:
        array= []
        for index in range(self.width):
            array+= self.matrice[index]
        return array
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

    m= Map(None, Trash(None), False)
    m.generate_chunks(Direction.fast("w"), 5)
    print(m.matrice)
    # print(m.find_blocks(lambda block: block == m.get_block(-4, -2)))

    # my_trash= Trash(None)
    # my_sorter= Sorter(None)
    # m.place(my_trash, Map.create_coordonates(5, 5))
    # m.place(my_sorter, Map.create_coordonates(5, 4))
    pass