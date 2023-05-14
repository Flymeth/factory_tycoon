class Quest:
    def __init__(self, game, title: str, description: str= "") -> None:
        from _main import Game

        self.game: Game= game
        self.title = title
        self.description = description
        self.done= False
        pass
    def is_compatible(self) -> bool:
        """ Renvoie si oui ou non (`True` ou `False`) la quête peut être applicable au joueur
        """
        return True
    def check_success(self) -> bool:
        """ Renvoie si oui ou non (`True` ou `False`) le joueur a accomplis cette quête
        """
        return False
    def give_reward(self) -> None:
        """ Done la récompense au joueur
        """
        return

# Note: les quetes seront misent dans l'ordre de leur définition

class FirstSelledItem(Quest):
    def __init__(self, game) -> None:
        super().__init__(game, "Your first quest", "Sell an item with the help of a query and a seller.")
    def check_success(self) -> bool:
        
        return super().check_success()