from pygame import font, freetype, Surface, Rect, Color
from typing import Literal

font.init()
freetype.init()

TITLE_FONT= freetype.Font("src/assets/fonts/octosquares.ttf", 24)
TITLE_FONT_BOLD= freetype.Font("src/assets/fonts/octosquares_bold.ttf", 24)
TEXT_FONT = freetype.Font("src/assets/fonts/made_infinity.otf", 12)

def auto_wrap(font: freetype.Font, font_size: int, text: str, max_width: int, align: Literal["left", "center", "right"] = "left", color: Color | tuple = (0, 0, 0)) -> tuple[Surface, Rect]:
    words= text.split(" ")
    wrapped: list[str]= [""]

    rect_width = 0
    rect_height= font_size
    
    for word in words:
        w_size = len(word)
        assert w_size <= max_width, "Max width is too low: text can't be wrapped."

        last_sentence= wrapped[-1]
        new_sentence = f"{last_sentence} {word}" if last_sentence else word
        width, height = font.render_raw(new_sentence, size= font_size)[1]
        breaking_required= width > max_width

        if breaking_required:
            wrapped.append(word)
            rect_height+= height
        else:
            wrapped[-1]= new_sentence
            if width > rect_width: rect_width = width
    
    rect= Rect(0, 0, rect_width, rect_height)
    result= Surface(rect.size)

    y = 0
    for sentence in wrapped:
        rendered_text, rendered_rect= font.render(sentence, fgcolor= color, size= font_size)

        x = 0 if align == "left" else rect.centerx - rendered_rect.width/2 if align == "center" else rect.width - rendered_rect.width
        result.blit(rendered_text, (x, y))
        y+= rendered_rect.height
    
    return result, rect
