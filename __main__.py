import sdl2
import pyaudio
import numpy

from operator  import itemgetter
from argparse  import ArgumentParser
from functools import partial
from ctypes    import pointer
from sys       import getdefaultencoding

# default system encoding to use, this is to encode SDL window's title.
str_encode = partial(str.encode, encoding= getdefaultencoding())

# this is to map FFT values of [0..+1] to actual screen coordinates.
maprange = lambda x, a,b, c,d: \
    (x - a) * (d - c) / (b - a) + c

class Spectro(ArgumentParser):
    """
    Spectro is a program to show spectrum of the audio recieved from a
    physcially external source outside of the host machine (eg. from a micrphone),
    its goal is to show which sinewaves roughly reconstruct the original wave
    and also some use it just for curiosity and enjoyment so enjoy!
    """

    def __init__(self):
        ArgumentParser.__init__(self,
            self.__class__.__name__,
            description= self.__doc__,
            allow_abbrev= True)

        self.add_argument('-width',
            type= int,
            required= True,
            help= "width of the visualiser window")

        self.add_argument('-height',
            type= int,
            required= True,
            help= "height of the visualiser window")

        self.add_argument('-bufsize',
            type= int,
            default= 1024,
            help= "number of PCM samples to retrieve per callback.\n"
                  "this affects the density of the spectrum")

        self.add_argument('-samplerate',
            type= int,
            default= 44100,
            help= "samplerate of the audio.\n"
                  "which controls the time-domain resolution")

        self.options = self.parse_args()
    
    def main(self):
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

        self.vwin = sdl2.SDL_CreateWindow(
                    str_encode(self.__class__.__name__),
                    sdl2.SDL_WINDOWPOS_CENTERED,
                    sdl2.SDL_WINDOWPOS_CENTERED,
                    self.options.width, self.options.height, 0)
        vrend = sdl2.SDL_CreateRenderer(self.vwin, -1, 0)

        
        num_tdbins  = self.options.bufsize
        num_fftbins = num_tdbins // 2
        fftbins     = pointer((sdl2.SDL_Point * num_fftbins)())
        _slicewidth = self.options.width / num_fftbins

        def _visualiser(frames, num_frames, *_):
            sdl2.SDL_SetRenderDrawColor(vrend, 0x20, 0x0f, 0x7f, 0xff)
            sdl2.SDL_RenderClear(vrend)

            sdl2.SDL_SetRenderDrawColor(vrend, 0x7f, 0xff, 0x40, 0xff)

            fftdata = (numpy.abs(
                        numpy.fft.rfft(
                            memoryview(frames).cast('f') * numpy.hamming(num_tdbins)
                        )) / num_fftbins)[:num_fftbins]     
       
            x, y = 0.0, 0.0
            for idx, fbin in enumerate(fftdata):
                # map value as: 1 = top, 0 = bottom.
                y = maprange(fbin, 0, 1, self.options.height, 0)
                fftbins.contents[idx] = sdl2.SDL_Point(int(x), int(y))
                x+= _slicewidth

            sdl2.SDL_RenderDrawLines(vrend, fftbins.contents, num_fftbins)
            sdl2.SDL_RenderPresent(vrend)

            return (frames, pyaudio.paContinue)

        self.aout = pyaudio.PyAudio().open(
            rate= self.options.samplerate,
            channels= 1, format= pyaudio.paFloat32,
            input= True, output= True,
            frames_per_buffer= self.options.bufsize,
            stream_callback= _visualiser)
        
        self.aout.start_stream()

if __name__ == "__main__":
    app = Spectro()
    app.main()

    dispevt = sdl2.SDL_Event()
    while True:
        sdl2.SDL_PollEvent(dispevt)
        if dispevt.type == sdl2.SDL_QUIT:
            app.aout.stop_stream()
            sdl2.SDL_DestroyWindow(app.vwin)
            break
