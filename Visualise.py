# This library provides a Canvas to draw the spectrum on.
# Isn't very advanced. But, simple to use.
# I'm may implement pygame in future.
import sdl2

# An "Cooley-Tukey FFT" implementation of SciPy.
# Computes a one dimensional "Discrete Fourier Transform".
# This is the secret ingridient to make spectrum visualiser.
from scipy.fftpack import fft

# Utilities that make possible to draw the spectrum.
from numpy import abs as fft_abs
from ctypes import pointer
from math import log10

# Maximum numeric value of each bin in the FFT spectrum.
# Scaled to 255 to suit convolutions.
FFT_VAL_MAX = 255


def maprange(x: float, min: tuple, max: tuple):
    (a, b) = min # a: input minimum, b: input maximum
    (c, d) = max # c: output minimum, b: output maximum
    
    return ((x - a) * ((d - c) / (b - a))) + c

# # Minimum dynamic range (expressed in decibels). The hearing dynamic
# # range of humans is 120dB.
# MIN_DB = -(120)

class Visualiser():
    # This stores the magnitude data of the FFT spectrum.
    _fft_spectrum: list = []
    _fft_bins: int = 0

    # A list of (vertical, horizontal) coordinates to shape a Path.
    _data_points = None

    def __init__(
        self,
        width: int,
        height: int,
        fft_bins: int # Number of bins in a FFT spectrum.
    ):
        # The object creates interacts with Window Manager of the OS.
        # And displays the rendered pixel data in Window.
        # Width and Height are dynamic (must overflow the Display size).
        self._window = sdl2.SDL_CreateWindow(
            b"Visualiser",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            width,
            height,
            0
        )

        # Renderer draws rasterizes the data to pixels to be
        # displayed on the screen. (Doesn't support Float precision).
        self._renderer = sdl2.SDL_CreateRenderer(
            self._window,
            0, sdl2.SDL_RENDERER_ACCELERATED
        )

        # Stores severeal information about events get emitted
        # in SDL2. Mainly required to detect "Window Close".
        self._event = sdl2.SDL_Event()

        # Create several SDL_Point objects which store the coordinates
        # of the path.
        self._data_points = pointer((sdl2.SDL_Point * fft_bins)())
        self._bar_width = width / fft_bins
        self._viewport = {
            'width': width,
            'height': height
        }
        self._fft_bins = fft_bins

    def getrefs(self):
        # Return all the SDL object refrences in a dictionary.
        # This feature might be required in future.
        return {
            "window": self._window,
            "renderer": self._renderer,
            "event": self._event 
        }

    def draw(
        self,
        waveform: list,
        colors: tuple # background and foreground colors
    ):
        # Do a one-dimensional Discrete Fourier Transform on the waveform.
        # Slice it to half because of the nyquist theorem.
        # This FFT outputs each bin with numeric range of [-255..255]
        self._fft_spectrum = fft(waveform)[:self._fft_bins]
        
        # x = 0
        for idx in range(len(self._fft_spectrum)):
            self._data_points.contents[idx] = sdl2.SDL_Point(
                # round(x),
                int(maprange(
                    list(self._fft_spectrum.imag)[idx],
                    (-255, 255),
                    (0, self._viewport['width'])
                )),
                # "y" value going in positive direction apart from 0
                # represents going down the screen.
                # So BIN_MIN represents the Height value and BIN_MAX value (0).
                # int(maprange( 20 * log10(val), (MIN_DB, 0), (self._viewport['height'], 0) ))
                 int(maprange(
                    list(self._fft_spectrum.real)[idx],
                    (-255, 255),
                    (0, self._viewport['height'])
                ))
            )
            # x+= self._bar_width

        # Draw the color for the background of the Canvas.
        sdl2.SDL_SetRenderDrawColor(
            self._renderer,
            colors[0][0], colors[0][1], colors[0][2], colors[0][3]  
        )
        sdl2.SDL_RenderClear(self._renderer)

        # Draw a path based on points and color it as foreground.
        sdl2.SDL_SetRenderDrawColor(
            self._renderer,
            colors[1][0], colors[1][1], colors[1][2], colors[1][3]
        )
        sdl2.SDL_RenderDrawLines(
            self._renderer,
            self._data_points.contents, self._fft_bins
        )
        sdl2.SDL_RenderPresent(self._renderer)

        # Know if the user quits from the program.
        sdl2.SDL_PollEvent(self._event)
        if self._event.type == sdl2.SDL_QUIT:
            return True

    # When this functions is called the Renderer and Window
    # are destructed.
    # By default, this function doesn't executes internally.
    # Must be called explicitly to close SDL_Window.
    def close(self):
        sdl2.SDL_DestroyRenderer(self._renderer)
        sdl2.SDL_DestroyWindow(self._window)