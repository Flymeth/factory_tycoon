class Direction:
    North= 0
    East= 1
    South= 2
    West= 3

    typeof= list[int] | int

    @staticmethod
    def stringify(direction: int) -> str:
        assert type(direction) == int and 0 <= direction <= 3, "Invalid direction provided"
        for key in dir(Direction):
            if getattr(Direction, key) == direction:
                return key.lower()
    @staticmethod
    def listify(directions: list[int] | int) -> list[int]:
        return directions if type(directions) == list else [directions]
    @staticmethod
    def fast(direction: str= "") -> list[int]:
        """
            ----------------------------------------
            'a' -> all direction (equivalent to 'nswe')
            'h' -> horizontaly (equivalent to 'we')
            'v' -> verticaly (equivalent to 'ns')
            'x' -> static (equivalent to '') (default)

            Can't be combined
            ----------------------------------------
            'n' -> north
            's' -> south
            'w' -> west
            'e' -> east

            Can be combined like 'sn', 'nse', ...
            ----------------------------------------
        """
        if direction == "": return []
        dir_len= len(direction)
        combinable= not (direction in "avhx")
        assert 0 < dir_len <= 4, "Direction input must have between 1 and 4 letters"
        assert combinable or dir_len == 1, "Incombinable letter has been combined"
        if combinable:
            if dir_len > 1: return [Direction.fast(letter) for letter in direction]
            return {
                "n": Direction.North,
                "s": Direction.South,
                "e": Direction.East,
                "w": Direction.West
            }[direction]
        else:
            return {
                "a": lambda: Direction.fast("nesw"),
                "h": lambda: Direction.fast("ew"),
                "v": lambda: Direction.fast("ns"),
                "x": lambda: Direction.fast("")
            }[direction]()

if __name__ == "__main__":
    print(Direction.stringify(2))
    print(Direction.fast())
    print(Direction.fast("h"))
    print(Direction.fast("sw"))
    print(Direction.fast("we"))
    print(Direction.fast("x"))