import sdl2
from numpy.fft import fft
from numpy import abs as fft_abs
from ctypes import pointer
from constants import NP_FFT_MAXVAL

# Maps a real number in range into another real number into another range.
maprange = lambda x, a, b, c, d: ((x - a) * ((d - c) / (b - a))) + c

class Visualiser():
    # This stores the magnitude data of the FFT spectrum.
    fft_spectrum: list = []
    fft_bins: int = 0

    # A list of (vertical, horizontal) coordinates to shape a Path.
    data_points = None

    def __init__(
        self,
        width: int,
        height: int,
        fft_bins: int # Number of bins in a FFT spectrum.
    ):
        # The object creates interacts with Window Manager of the OS.
        # And displays the rendered pixel data in Window.
        # Width and Height are dynamic (must overflow the Display size).
        self.window = sdl2.SDL_CreateWindow(
            b'',
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            width,
            height,
            sdl2.SDL_RENDERER_ACCELERATED
        )

        # Renderer draws rasterizes the data to pixels to be
        # displayed on the screen. (Doesn't support Float precision).
        self.renderer = sdl2.SDL_CreateRenderer(
            self.window,
            0, sdl2.SDL_RENDERER_ACCELERATED
        )

        # Stores severeal information about events get emitted
        # in SDL2. Mainly required to detect "Window Close".
        self.event = sdl2.SDL_Event()

        # Create several SDL_Point objects which store the coordinates
        # of the path.
        self.data_points = pointer((sdl2.SDL_Point * fft_bins)())
        self.bar_width = width / fft_bins
        self.viewport = {
            'width': width,
            'height': height
        }
        self.fft_bins = fft_bins

    def getrefs(self):
        # Return all the SDL object refrences in a dictionary.
        # This feature might be required in future.
        return {
            "window": self.window,
            "renderer": self.renderer,
            "event": self.event
        }

    def draw(
        self,
        waveform: list,
        colors: tuple # background and foreground colors
    ):
        # Compute a Fourier Transform on the Waveform to
        # divide the sound into several "bins". To
        # visualise them as points on the render window.
        self.fft_spectrum = fft_abs(fft(waveform))[:self.fft_bins]

        x = 0 # reset the coordinate on each call
        for idx, bin in enumerate(self.fft_spectrum):
            self.data_points.contents[idx] = sdl2.SDL_Point(
                round(x),
                int(maprange(
                    bin,
                    0, NP_FFT_MAXVAL,
                    0, self.viewport['width']
                ))
            )
            x+= self.bar_width

        # Clear the canvas with our selected colour.
        # What it does is repaints the screen
        # the previous frame is overlapped by it.
        sdl2.SDL_SetRenderDrawColor(
            self.renderer,
            colors[0][0], colors[0][1], colors[0][2], colors[0][3]
        )
        sdl2.SDL_RenderClear(self.renderer)

        # Draw the visualization using connected paths which
        # are stroked. When percepted they represent themeselves
        # as "lines".
        sdl2.SDL_SetRenderDrawColor(
            self.renderer,
            colors[1][0], colors[1][1], colors[1][2], colors[1][3]
        )
        sdl2.SDL_RenderDrawLines(
            self.renderer,
            self.data_points.contents, self.fft_bins
        )
        
        # Display the contents on the screen which
        # was rendered off-screen.
        sdl2.SDL_RenderPresent(self.renderer)

        # Look for the event when the user closes
        # the render window.
        sdl2.SDL_PollEvent(self.event)
        if self.event.type == sdl2.SDL_QUIT:
            self.close()
            return True

    # Closes the render window. And sends a quit signal
    # to the main program.
    def close(self):
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)
