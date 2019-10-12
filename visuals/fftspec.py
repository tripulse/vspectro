from sdl2 import SDL_Point
from ctypes import pointer
from numpy.fft import rfft
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
                                    / n_samples

        # Allocates the datapoints to place the spectrum
        # data in to later visualise it.
        self.datapoints = pointer((SDL_Point * self.config['n_fftbins'])())

    def compute(
        self,
        waveform: tuple,
        vp_scaling: int
    ):
        fft_data = list(norm(rfft(waveform)) \
            [:self.config['n_fftbins']])

        x = y = 0 #< coordinates of each point
        for idx in range(self.config['max_datapoints']):
            y = fft_data[idx]

            self.datapoints.contents[idx] = SDL_Point(
                round(x),
                int(maprange(
                    y,
                    -NP_FFT_MAXVAL, NP_FFT_MAXVAL,
                    0, vp_scaling
            )))

            x += self.config['slice_width']

        # Standard callback return format specified by:
        # ../src/visualise.py
        return (self.datapoints, self.config['n_fftbins'])