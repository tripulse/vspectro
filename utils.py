from sdl2 import SDL_Event, SDL_PollEvent
def SDL_IsEventOccured(event_type: int):
    """
    Polls for whether the event passed has been occured or not.
    True if occured, False if not.
    """
    _event = SDL_Event()
    SDL_PollEvent(_event)

    return event_type == _event.type