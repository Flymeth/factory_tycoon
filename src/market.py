class Market:
    def __init__(self, game) -> None:
        from _main import Game

        self.game: Game= game
        self.courts: dict[str, float] = {} # {item_type: court_value}
        self.shop = {}
        pass