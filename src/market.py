class Market:
    def __init__(self, game) -> None:
        self.game= game
        self.courts: dict[str, float] = {} # {item_type: court_value}
        self.shop = {}
        pass