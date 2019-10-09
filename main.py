# This is the root file of the project.
# If you want to add a feature (use it here).

import pyaudio
from struct import Struct
import configparser
import Visualise
from constants import *
from chalk import red, green
from yaml import load, CLoader

# Parses the configuration file corresponding to this program.
# And uses properties of it in several aspects of it.
_configs = yaml.loads("configs/general.yml", Loader=CLoader)

# Number of frequency bins returned by the
# Fourier Transform.
_configs['audioIO']['fftBins'] = int(_configs['audioIO']['bufferSize'] / 2)

# Opens an interface to PortAudio to recieve audio
# data from AUX input.
pcm_grabber = pyaudio.PyAudio()
vis = Visualise.Visualiser(
    _configs['viewport']['width'],
    _configs['viewport']['height'],
    fftBins
)


# Maximum number of devices for I/O operation via the Host API.
# TODO: fix the lagging of device selection feature
maximum_device = pcm_grabber.get_device_count()

# List all the devices supported by the Host API.
# Selection is not avialable due to regressions (would be fixed later).
for device_index in range(maximum_device):
    device_info = pcm_grabber.get_device_info_by_index(device_index)

    print(
        "[%d %s%s] %s" % (
            device_info['index'],
            green("I") if device_info['maxInputChannels'] else str(),
            red("O") if device_info['maxOutputChannels'] else str(),
            device_info['name']
        )
    )


# Unpacker which is construcuted only to decode
# Float32 data from octets using native byte-order.
_unpacker = Struct("=f")

def _process_audio(frames, nFrames, timeInfo, status):
    audio_buffer = list(
        map(
            lambda sample: sample[0], # iter_unpack returns each item wrapped
                                      # in a tuple. hence, we've to unpack
                                      # it manually.
            _unpacker.iter_unpack(frames)
        )
    )


    # (bg_color) is background, (fg_color) is foreground.
    # defition of color palettes are given above this
    # function and explained in detail.
    isClosed = vis.draw(audio_buffer, (bg_color, fg_color))

    # If the UI encounters a close event abort
    # the PyAudio stream too.
    if isClosed:
        return (bytes(), pyaudio.paComplete)

    return (bytes(), pyaudio.paContinue)

# Open a full-duplex stream which can output and input.
# We pipe input to output. And visuailse the Input as FFT spectrum.
try:
    pcm_stream = pcm_grabber.open(
        _configs['audioIO']['sampleRate'],
        1, pyaudio.paFloat32,
        input= True,
        stream_callback= _process_audio,
        frames_per_buffer= _configs['audioIO']['bufferSize'],
        # NOTE: This feature has been turned off. Because, it lags on WINDOWS.
        # input_device_index= selected_device
    )
except OSError:
    print(red(
        "Encountered problems while intializing Input device(s).",
    )); exit()

from time import sleep
pcm_stream.start_stream()

# Hook-up this code until input device
# gets disconnected.
while pcm_stream.is_active():
    sleep(LOOKFOR_STREAMCLOSE)

pcm_stream.stop_stream()
pcm_stream.close()
