from pygame import USEREVENT

__id__= 0
def new():
    global __id__
    __id__+= 1
    return USEREVENT + __id__

DRAW_EVENT = TICK_EVENT = new()
PROCESS_EVENT = new()
LEFT_CLICK = new()
MIDDLE_CLICK = new()
RIGHT_CLICK = new()