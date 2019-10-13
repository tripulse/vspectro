from sdl2 import SDL_Event, SDL_PollEvent

def SDL_IsEventOccured(event_type: int):
    """
    Looks up for a SDL event. If event isn't triggered then `False`
    otherwise `True`.
    """
    _event = SDL_Event()
    SDL_PollEvent(_event)

    return event_type == _event.type