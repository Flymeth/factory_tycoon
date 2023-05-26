from pygame import image, Surface, SRCALPHA
from os.path import exists
cache: dict[str, Surface]= {}

def create_surface(texture_path: str) -> Surface:
    if not (texture_path and exists(texture_path)): texture_path= "src/assets/no_texture.png"
    return image.load(texture_path, f"Image at path {texture_path}").convert_alpha()

def get_texture(texture_category: str, texture_name: str) -> Surface:
    texture_path= f"src/assets/{texture_category}/{texture_name}.png" if texture_category and texture_name else ""
    if texture_path in cache:
        return cache[texture_path]
    else:
        texture= create_surface(texture_path)
        cache[texture_path]= texture
        return texture