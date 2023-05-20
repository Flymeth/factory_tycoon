from pygame import colordict, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEWHEEL, mouse, event, display
from font import TEXT_FONT

ZOOM_SPEED: int= 5
MOVING_BUTTON_ID: int= 2 # 2 = wheel_button
class Camera():
    def __init__(self, game, position: list[float, float]= [0, 0], zoom: float= 100) -> None:
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
        from _main import Game

        self.game: Game = game
        self.position= position
        self.zoom= zoom
        self.moving_camera= False
        self.game.add_event(MOUSEBUTTONUP, lambda g,e: self.handle_mouse_pressures(e.button, False))
        self.game.add_event(MOUSEBUTTONDOWN, lambda g,e: self.handle_mouse_pressures(e.button, True))
        self.game.add_event("tick", lambda g,e: self.handle_camera_movements())
        self.game.add_event(MOUSEWHEEL, lambda g,e: self.handle_camera_zoom(e.y))
    @property
    def screen_center(self):
        return [size /2 for size in display.get_window_size()]
    def handle_mouse_pressures(self, button: int, is_pressed: bool):
        self.moving_camera= is_pressed and button == MOVING_BUTTON_ID
        if self.moving_camera: mouse.get_rel()
        elif not is_pressed and button == MOVING_BUTTON_ID:
            mouse.set_pos(self.screen_center)
    def handle_camera_movements(self):
        mouse.set_visible(not self.moving_camera)
        event.set_grab(self.moving_camera)
        if self.moving_camera:
            rel= mouse.get_rel()
            self.position= [
                self.position[i] - rel[i]
                for i in range(2)
            ]
    def handle_camera_zoom(self, wheeling_y: float):
        self.zoom= min(200, max(20, self.zoom + wheeling_y * ZOOM_SPEED))
        pass
    def get_screen_position(self, coordonates: tuple[int, int]):
        screen_size= self.game.pygame.screen.get_size()
        return [
            (coordonates[i] - self.position[i]/100 - 1) * self.zoom 
            + (screen_size[i] + self.zoom)/2
            for i in range(2)
        ]
    def get_screen_center_coordonates(self):
        signof= lambda x: (x < -1) * -2 + 1 # = the sign of the argument

        return [
            -int((
                self.position[i]
                + self.zoom
                / 2 * signof(self.position[i])
            )/ self.zoom) # It works, but idk how
            for i in range(2)
        ]
    def get_cursor_coordonates(self):
        mouse_pos= mouse.get_pos()
        screen_size = display.get_window_size()
        x, y = [(mouse_pos[i]/screen_size[i])*2 -1 for i in range(2)]
        print(x, y)
        pass
    def draw(self):
        self.game.pygame.screen.fill(colordict.THECOLORS["purple"])
        self.get_cursor_coordonates()
        drawed= 0
        for block in self.game.map.flatten():
            if block.draw(): drawed+= 1
        if self.game.DEV_MODE:
            TEXT_FONT.render_to(self.game.pygame.screen, (10, 10), f"Camera position: {self.position}", (0, 0, 0))
            TEXT_FONT.render_to(self.game.pygame.screen, (10, 30), f"FPS: {round(self.game.pygame.clock.get_fps(), 3)}", (0, 0, 0))
            TEXT_FONT.render_to(self.game.pygame.screen, (10, 40), f"Drawed blocks: {drawed}", (0, 0, 0))
            TEXT_FONT.render_to(self.game.pygame.screen, self.screen_center, f"\\", (0, 0, 0), size=0)