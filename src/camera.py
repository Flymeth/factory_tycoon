from pygame import colordict, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEWHEEL, mouse, event, display, KEYDOWN, KEYUP, K_UP, K_DOWN, K_RIGHT, K_LEFT, K_KP_PLUS, K_KP_MINUS
from fonts import TEXT_FONT
from math import ceil, floor
from custom_events_identifier import TICK_EVENT, DRAW_EVENT

ZOOM_SPEED: int= 5
MOVING_BUTTON_ID: int= 2 # 2 = wheel_button
signof= lambda x: (x < -1) * -2 + 1 # = the sign of the argument

directions_keys = {
    K_UP: (0, 1),
    K_DOWN: (0, -1),
    K_RIGHT: (1, 0),
    K_LEFT: (-1, 0)
}
zoom_keys = {
    K_KP_PLUS: 1,
    K_KP_MINUS: -1
}
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
        self.game.add_event(TICK_EVENT, lambda g,e: self.handle_camera_movements())
        self.game.add_event(DRAW_EVENT, lambda g,e: self.draw())
        self.game.add_event(MOUSEWHEEL, lambda g,e: self.handle_camera_zoom(e.y))

        self.key_movements= {
            "position": [],
            "zoom": 0
        }
        self.game.add_event(KEYDOWN, lambda g, e: self.key_down(e.key))
        self.game.add_event(KEYUP, lambda g, e: self.key_up(e.key))
        self.min_max_zoom= (30, 200)
        self.min_max_position= [
            (-50000, 50000),
            (-50000, 50000)
        ]
        self.freeze_position= False
        self.freeze_zoom= False
        self.mouse_position_before_cam_movement= None
    @property
    def screen_center(self):
        return [size /2 for size in display.get_window_size()]
    def handle_mouse_pressures(self, button: int, is_pressed: bool):
        self.moving_camera= is_pressed and button == MOVING_BUTTON_ID and not self.freeze_position
        if self.moving_camera: mouse.get_rel()
        elif not is_pressed and button == MOVING_BUTTON_ID and self.mouse_position_before_cam_movement:
            mouse.set_pos(self.mouse_position_before_cam_movement)
            self.mouse_position_before_cam_movement= None
    def key_down(self, key: int):
        if key in directions_keys:
            self.key_movements["position"].append(directions_keys[key])
        if key in zoom_keys and not self.key_movements["zoom"]:
            self.key_movements["zoom"]= zoom_keys[key]
    def key_up(self, key: int):
        if key in directions_keys:
            self.key_movements["position"].remove(directions_keys[key])
        if key in zoom_keys:
            self.key_movements["zoom"]= 0
    def handle_camera_movements(self):
        mouse.set_visible(not self.moving_camera)
        event.set_grab(self.moving_camera)

        if self.key_movements["zoom"]:
            self.handle_camera_zoom(self.key_movements["zoom"])

        if self.key_movements["position"]:
            direction = [0, 0]
            for x, y in self.key_movements["position"]:
                direction[0]+= x
                direction[1]+= y
            torc= (self.min_max_zoom[1] - self.zoom) /10
            self.set_camera_position(
                self.position[0] + direction[0] * torc,
                self.position[1] + direction[1] * torc
            )
        elif self.moving_camera:
            if not self.mouse_position_before_cam_movement:
                self.mouse_position_before_cam_movement= mouse.get_pos()

            rel= list(mouse.get_rel())
            rel[1]*= -1
            self.set_camera_position(
                self.position[0] - rel[0],
                self.position[1] - rel[1]
            )
    def set_camera_position(self, x: float, y: float):
        if self.freeze_position: return
        self.position= [
            min(self.min_max_position[i][1], max(self.min_max_position[i][0], (x, y)[i]))
            for i in range(2)
        ]
        if self.game.DEV_MODE:
            print(f"SET POSITION TO: {self.position}")
    def set_camera_zoom(self, new_zoom: float):
        if self.freeze_zoom: return
        self.zoom= min(self.min_max_zoom[1], max(self.min_max_zoom[0], new_zoom))
        if self.game.DEV_MODE:
            print(f"SET ZOOM TO: {self.zoom}px")
    def handle_camera_zoom(self, wheeling_y: int):
        self.set_camera_zoom(self.zoom + wheeling_y * ZOOM_SPEED)
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
            for pos in (self.position[0], -self.position[1])
        ]

        x, y = [
            int((
                position[i]
                + self.zoom/2 * signof(position[i])
            )/ self.zoom) # It works, but idk how
            for i in range(2)
        ]
        return x, -y
    def get_cursor_coordonates(self):
        mouse_pos= mouse.get_pos()
        screen_size = display.get_window_size()
        centered_mouse_position= [
            mouse_pos[i] - screen_size[i]/2
            for i in range(2)
        ]
        position = [
            pos / 100 * self.zoom
            for pos in (self.position[0], -self.position[1])
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
        assert self.game, "Cannot draw without the game object"
        self.game.pygame.screen.fill(colordict.THECOLORS["gray20"])
        center_x, center_y= self.get_screen_center_coordonates()
        screen_w, screen_h= display.get_window_size()
        max_fittable_blocks= ceil(screen_w /self.zoom) +1, ceil(screen_h /self.zoom) +1
        ranges= {
            "x": [
                int(
                    center_x + max_fittable_blocks[0]//2 * (i - 1) # ==> (i - 1) <=> [-1] pour le 1e élément et [+1] pour le second (permet de faire en sorte que le "+" se transforme en "-")
                    + .5 * i # ==> Ajoute 1 si c'est le 2nd élément (car le range ne prendra pas le dernier élément)
                )
                for i in (0, 2)
            ],
            "y": [
                int(
                    center_y + max_fittable_blocks[1]//2 * (i - 1) # ==> Voir les explications ci-dessus
                    + .5 * i # ==> Voir les explications ci-dessus
                )
                for i in (0, 2)
            ]
        }
        drawed= 0
        def draw_block(x: int, y: int):
            block = self.game.map.get_block(x, y)
            return block.draw() if block else None
        for x in range(*ranges["x"]):
            for y in range(*ranges["y"]):
                if draw_block(x, y):
                    drawed+= 1
        if self.game.DEV_MODE:
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 5), f"FPS: {round(self.game.pygame.clock.get_fps(), 2)}", (255, 255, 255))
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 20), f"DRAWED BLOCKS: {drawed}", (255, 255, 255))
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 35), f"POINTED COORDONATES: {self.get_cursor_coordonates()}", (255, 255, 255))
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 50), f"POSITION: {self.position}", (255, 255, 255))
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 65), f"SCREEN CENTER BLOCK: {(center_x, center_y)}", (255, 255, 255))
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 80), f"PRINT RANGE: {(ranges['x'][0], ranges['y'][0])}, {(ranges['x'][1], ranges['y'][1])}", (255, 255, 255))
            TEXT_FONT.render_to(self.game.pygame.screen, (5, 95), f"CREDIT: {self.game.player.balance}", (255, 255, 255))
