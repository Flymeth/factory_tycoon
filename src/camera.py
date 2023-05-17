from pygame import colordict
class Camera():
    def __init__(self, game, position: tuple[float, float]= (0, 0), zoom: float= 128) -> None:
        """            
            Zoom
                Le zoom correspond à la largeur des cases/blocks (en px)
            Position
                Correspond à la position de la caméra par rapport au block centrale de la map
        """
        assert game, "Cannot init the camera without the game property"
        from _main import Game

        self.game: Game = game
        self.position= position
        self.zoom= zoom
    def get_screen_position(self, map_position: tuple[int, int]):
        screen_center= self.position
        x, y= [
            (int(screen_center[i]) - map_position[i]*self.zoom)
            for i in range(2)
        ]
        screen_w, screen_h= self.game.pygame.screen.get_size()
        return x/screen_w + screen_w/2 - self.zoom/2, y/screen_h + screen_h/2 - self.zoom/2
    def get_pointed_block(self):
        return self.game.map.get_block(*[int(coord) for coord in self.position])

    def draw(self):
        self.game.pygame.screen.fill(colordict.THECOLORS["purple"])
        self.zoom-= .25 # For testing
        for block in self.game.map.flatten():
            block.draw(self.game)
        
        