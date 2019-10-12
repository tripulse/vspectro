from sdl2 import SDL_Point
from ctypes import pointer
from numpy.fft import fft
from numpy import abs as norm
from comps.constants import NP_FFT_MAXVAL

maprange = lambda x, a, b, c, d: \
            ((x - a) * ((d - c) / (b - a))) + c

class FFTSpectrum():
    # All the configuration of applying FFT transform.
    config = {}

    def __init__(
        self,
        n_samples: int,
        max_datapoints: int
    ):
        # Number of bins to use from the FFT spectrum.
        # As of the nyquist, samplerate must be
        # double of the maximum frequency.
        self.config['n_fftbins'] = int(n_samples/2)
        self.config['max_datapoints'] = max_datapoints
        self.config['slice_width'] = max_datapoints \
                                    / self.config['n_fftbins']

        # Allocates the datapoints to place the spectrum
        # data in to later visualise it.
        self.datapoints = pointer((SDL_Point * self.config['n_fftbins'])())

    def compute(
        self,
        waveform: tuple,
        vp_scaling: int
    ):
        fft_data = norm(fft(waveform)) \
            [:self.config['n_fftbins']]

        (x, y) = (0, 0) #< inital coordinates, later used to store them
        for idx, bin in enumerate(fft_data):
            self.datapoints.contents[idx] = SDL_Point(
                round(x),
                int(maprange(
                    bin,
                    0, NP_FFT_MAXVAL,
                    vp_scaling, 0
            )))

            x += self.config['slice_width']

        # Standard callback return format specified by:
        # ../src/visualise.py.
        # A tuple of (datapoints, count of datapoints)
        return (self.datapoints.contents, self.config['n_fftbins'])