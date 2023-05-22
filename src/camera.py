from pygame import colordict, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEWHEEL, mouse, event, display
from font import TEXT_FONT

ZOOM_SPEED: int= 5
MOVING_BUTTON_ID: int= 2 # 2 = wheel_button
signof= lambda x: (x < -1) * -2 + 1 # = the sign of the argument

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
            rel= list(mouse.get_rel())
            rel[1]*= -1
            self.position= [
                self.position[i] - rel[i]
                for i in range(2)
            ]
    def handle_camera_zoom(self, wheeling_y: float):
        self.zoom= min(200, max(20, self.zoom + wheeling_y * ZOOM_SPEED))
        pass
    def get_screen_position(self, coordonates: tuple[int, int]):
        """ Returns the x & y position of the block in the screen where x and y is the top of the block
        """
        screen_size= display.get_window_size()
        coordonates= coordonates[0], coordonates[1]*-1 # Because for the screen, go upper means to decrease the y axis
        position = self.position[0], self.position[1]*-1
        x, y= [
            (coordonates[i] - position[i]/100) * self.zoom
            + (screen_size[i] - self.zoom)/2
            for i in range(2)
        ]
        return x, y
    def get_screen_center_coordonates(self):
        position = [
            pos / 100 * self.zoom
            for pos in self.position
        ]

        x, y = [
            int((
                position[i]
                + self.zoom/2 * signof(position[i])
            )/ self.zoom) # It works, but idk how
            for i in range(2)
        ]
        return x, y
    def get_cursor_coordonates(self):
        mouse_pos= mouse.get_pos()
        screen_size = display.get_window_size()
        centered_mouse_position= [
            mouse_pos[i] - screen_size[i]/2
            for i in range(2)
        ]
        position = [
            pos / 100 * self.zoom
            for pos in self.position
        ]

        x, y = [
            int((
                centered_mouse_position[i] + position[i]
                + self.zoom/2 * signof(centered_mouse_position[i] + position[i])
            ) /self.zoom) # same as above: it works, but idk how
            for i in range(2)
        ]
        return x, -y
    def draw(self):
        self.game.pygame.screen.fill(colordict.THECOLORS["purple"])
        center_x, center_y= self.get_screen_center_coordonates()
        drawed= 0
        
        def draw_block(x: int, y: int):
            block = self.game.map.get_block(x, y)
            return block.draw() if block else None
        for x_coef in (-1, 0, 1):
            x = center_x + x_coef
            while draw_block(x, center_y): # While the block in the x axis can be drawed
                drawed+= 1
                for y_coef in (-1, 1):
                    y = center_y + y_coef
                    while draw_block(x, y): # While the block in the y axis can be drawed
                        drawed+= 1
                        y+= y_coef # Move to the next block (verticaly)
                
                if not x_coef: break
                x+= x_coef # Move to the next block (horizontaly)
        if self.game.DEV_MODE:
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 5), f"FPS: {round(self.game.pygame.clock.get_fps(), 2)}", (255, 255, 255))
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 20), f"DRAWED BLOCKS: {drawed}", (255, 255, 255))
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 35), f"POINTED COORDONATES: {self.get_cursor_coordonates()}", (255, 255, 255))
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 50), f"POSITION: {self.position}", (255, 255, 255))