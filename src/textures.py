from pygame import image, Surface
cache: dict[str, Surface]= {}

def get_texture(texture_category: str, texture_name: str) -> Surface:
    texture_path= f"src/assets/{texture_category}/{texture_name}.png"
    if texture_path in cache:
        return cache[texture_path]
    else:
        texture= image.load(texture_path, f"{texture_name} img")
        cache[texture_path]= texture
        return texture