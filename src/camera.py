from pygame import colordict, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEWHEEL, mouse, event
class Camera():
    def __init__(self, game, position: list[float, float]= [0, 0], zoom: float= 128, blocks_gap= 0) -> None:
        """            
            Zoom
                Le zoom correspond à la largeur des cases/blocks (en px)
            Position
                Correspond à la position de la caméra par rapport au block centrale de la map
            Blocks Gap
                Correspond à la distance entre chaque block de la map
                Une valeur entre 0 et 1 est recommendée
        """
        assert game, "Cannot init the camera without the game property"
        assert blocks_gap >= 0, "Invalid blocks gap set"
        from _main import Game

        self.game: Game = game
        self.position= position
        self.zoom= zoom
        self.gap= 1+ blocks_gap
        self.moving_camera= False
        self.game.add_event(MOUSEBUTTONUP, lambda g,e: self.handle_mouse_pressures())
        self.game.add_event(MOUSEBUTTONDOWN, lambda g,e: self.handle_mouse_pressures())
        self.game.add_event("tick", lambda g,e: self.handle_camera_movements())
        self.game.add_event(MOUSEWHEEL, lambda g,e: self.handle_camera_zoom(e.y))

        event.set_grab(False)
    def handle_mouse_pressures(self):
        self.moving_camera= mouse.get_pressed()[2] # 2 = right_button
        if self.moving_camera: mouse.get_rel()
    def handle_camera_movements(self):
        mouse.set_visible(not self.moving_camera)
        if self.moving_camera:
            rel= mouse.get_rel()
            self.position= [
                self.position[i] - rel[i]
                for i in range(2)
            ]
    def handle_camera_zoom(self, wheeling_y: float):
        self.zoom= min(200, max(10, self.zoom + wheeling_y * 10))
        pass
    def get_screen_position(self, coordonates: tuple[int, int]):
        screen_center= self.position
        x, y= [
            ((coordonates[i] - 1)*self.zoom - int(screen_center[i]))
            for i in range(2)
        ]
        screen_w, screen_h= self.game.pygame.screen.get_size()

        pos_x= (screen_w + self.zoom)/2 + x * self.gap
        pos_y= (screen_h + self.zoom)/2 + y * self.gap
        return pos_x, pos_y
    def get_pointed_block(self):
        return self.game.map.get_block(*[int(coord) for coord in self.position])
    def draw(self):
        self.game.pygame.screen.fill(colordict.THECOLORS["purple"])
        for block in self.game.map.flatten():
            block.draw()
        
        