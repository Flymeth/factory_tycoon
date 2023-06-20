from pygame.mixer import Sound
from os.path import exists
cache: dict[str, Sound]= {}

def create_audio(audio_path: str) -> Sound:
    assert (audio_path and exists(audio_path)), f"Cannot load the audio from path '{audio_path}'"
    return Sound(audio_path)

def get_audio_path(audio_category: str, audio_name: str, ext = "wav") -> str:
    return f"src/assets/audio/{audio_category}/{audio_name}.{ext}" if audio_category and audio_name else ""

def get_audio(audio_category: str, audio_name: str, ext = "wav") -> Sound:
    audio_path= get_audio_path(audio_category, audio_name, ext)
    if audio_path in cache:
        return cache[audio_path]
    else:
        audio= create_audio(audio_path)
        cache[audio_path]= audio
        return audio