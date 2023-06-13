from pygame import image, Surface, SRCALPHA, transform, time
from os.path import exists
from moviepy.editor import VideoFileClip
cache: dict[str, Surface]= {}

class VideoSurface(Surface):
    def __init__(self, video_category: str, file_name: str, ext = "mp4", audio = False, size: tuple[int, int] | None= None):
        video_path = get_texture_path(video_category, file_name, ext)
        self.video= VideoFileClip(video_path, audio= audio)
        if not size:
            size: tuple[int, int]= self.video.size
        super().__init__(size)
    def update(self, speed: float = 1):
        curr_time = time.get_ticks()/1000 * speed
        max_time = self.video.duration * speed
        try:
            img = self.video.get_frame(curr_time % max_time)
            texture: Surface= image.frombuffer(img, self.video.size, "RGB")
        except:
            return
        self.fill((0, 0, 0))
        self.blit(
            transform.scale(texture, self.get_rect().size),
            (0, 0)
        )

def no_texture() -> Surface:
    return create_surface("src/assets/no_texture.png")

def new_blank_texture(size: tuple[int, int]) -> Surface:
    return Surface(size, SRCALPHA, 32).convert_alpha()

def create_surface(texture_path: str) -> Surface:
    if not (texture_path and exists(texture_path)): return no_texture()
    return image.load(texture_path, f"Image at path {texture_path}").convert_alpha()

def get_texture_path(texture_category: str, texture_name: str, ext = "png"):
    return f"src/assets/{texture_category}/{texture_name}.{ext}" if texture_category and texture_name else ""

def get_texture(texture_category: str, texture_name: str, ext = "png") -> Surface:
    texture_path= get_texture_path(texture_category, texture_name, ext)
    if texture_path in cache:
        return cache[texture_path]
    else:
        texture= create_surface(texture_path)
        cache[texture_path]= texture
        return texture