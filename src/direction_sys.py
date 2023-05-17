class Direction:
    North= 0
    East= 1
    South= 2
    West= 3

    single= int
    multiple= list[int]
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
    def rotate(initial: int, times_rotating_right: int = 0, times_rotating_left: int= 0):
        result= initial
        for _ in range(times_rotating_left): result = (result - 1)% 4
        for _ in range(times_rotating_right): result = (result + 1)% 4
        return result
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
        if not direction: return []
        dir_len= len(direction)
        combinable= not [letter for letter in direction if letter in "avhx"]
        assert 0 < dir_len <= 4, "Direction input must have between 1 and 4 letters"
        assert combinable or dir_len == 1, "Incombinable letter has been combined"
        if combinable:
            if dir_len > 1: return [Direction.fast(letter)[0] for letter in direction]
            return [
                {
                    "n": Direction.North,
                    "s": Direction.South,
                    "e": Direction.East,
                    "w": Direction.West
                }[direction]
            ]
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
    print(Direction.stringify(Direction.rotate(Direction.North, times_rotating_right=1)), Direction.East)