# code would be documented later on.
import pyaudio
from struct import iter_unpack
from time import sleep

class AudioIO():
    def __init__(
        self,
        sample_rate= 44100,
        channels= 1,
        buffer_size= 1024,
    ):
        self._config = {
            ['sampleRate']: abs(sample_rate),
            ['channels']: abs(channels),
            ['bufferSize']: abs(buffer_size)
        }

    # PortAudio's non-blocking Audio IO's
    # callback function which gets
    # triggered on when the API
    # recieves a frame of audio data.
    def set_callback(self, cb):
        # Callback must be a function and should
        # accept four arguments.
        self._callback = cb

    def _callback_wrapper(self, a,b,c,d):
        self._callback(a,b,c,d)


    def init(self):
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            rate= self._config['sampleRate'],
            channels= self._config['channels'],
            format= pyaudio.paFloat32,
            input= True,
            output= True,
            frames_per_buffer= self._config['bufferSize'],
            stream_callback= self._callback_wrapper
        )


    def start(self):
        self._stream.start_stream()
        self._loop()


    def _loop(self):
        while self._stream.is_active():
            sleep(1)
    
    def close(self):
        self._stream.close()