from sdl2 import SDL_Point
from ctypes import pointer
import numpy
import typing

maprange = lambda x, a,b, c,d: \
    (x - a) * (d - c) / (b - a) + c

class PlotDimensions(typing.NamedTuple):
    """
    Collection of limits of the datapoints' [X, Y] coordinates
    (width as maximum X, height as maximum Y).
    """
    width: int
    height: int

class FFTSpectrum:
    """
    A visualizer *built-in* plugin to transform waveforms into
    plotted FFT spectrum datapoints.
    """
    config: dict = {}

    def __init__(
        self,
        n_samples: int,
        max_datapoints: int,
        viewport: PlotDimensions
    ):
        self.config['n_fftbins'] = int(n_samples/2)
        self.config['max_datapoints'] = max_datapoints
        self.config['slice_width'] = max_datapoints / self.config['n_fftbins']
        self.config['viewport'] = viewport

        self.datapoints = pointer((SDL_Point * self.config['n_fftbins'])())

    def compute(
        self,
        waveform
    ):
        # Compute a Real-To-Complex FFT on the input signal and slice it half
        # to display only the required part of the frequency domain.
        fft_data = numpy.abs(numpy.fft.rfft(tuple(waveform)))[:self.config['n_fftbins']]

        (x, y) = (0, 0)
        for idx, bin in enumerate(fft_data):
            y = int(round(maprange(
                    bin,
                    0, 255, # TODO: find the correct range of the output!
                    self.config['viewport'].height, 0)))
            self.datapoints.contents[idx] = SDL_Point(round(x), round(y))
            x += self.config['slice_width']

        return {
            'datapoints': self.datapoints.contents,
            'length': self.config['n_fftbins']
        }