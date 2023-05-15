class Camera():
    def __init__(self, game, position: tuple[float]= (0, 0), zoom: float= 0) -> None:
        """            
            Zoom
                Le zoom correspond au nombre de blocks que le joueur peut voir sur une ligne de large
                    Ex:
                    zoom = 3
                    3 blocks prendront la totalité de la largeur de l'écran
            Position
                Correspond à la position de la caméra par rapport au block centrale de celle-ci
        """
        from _main import Game

        self.game: Game = game
        self.position= position
        self.zoom= zoom
    def draw(self):
        assert self.game, "Cannot draw without the game property"
        