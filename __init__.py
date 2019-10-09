# This is the root file of the project.
# If you want to add a feature (use it here).

import pyaudio
from struct import Struct
import configparser
import Visualise
from constants import *
from chalk import red, green


# Read the configuration file. Which defines the shape and basics
# of the program. The documentaion is written about the configuration
# file in Github repository Wiki.
configs = configparser.ConfigParser()
configs.read(CONFIG_FILE)

# Configuration that used to customize the application.
# Is stored in the configs/*.


# Constants which defines how Visualizer would act.
fftBins = int(int(configs['AudioIO']['BufferSize'])/2)

# This class lets us access the PortAudio API. To stream or record the
# audio data. As 32-bit Floating Point precision.
pcm_grabber = pyaudio.PyAudio()
vis = Visualise.Visualiser(
    int(configs['Viewport']['Width']),
    int(configs['Viewport']['Height']),
    fftBins
)

# List the input the devices avialable on the device.
# Print some information about each device too.

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

# Color palette are added into code to decorate the Visualization.
# Thanks to, `colorhunt.co` for some of the great color palettes.
color_palettes = [
    #       Foreground                Background
    [[0x00, 0xad, 0xb5, 0xff], [0x22, 0x28, 0x31, 0xff]], # Green-Darkblue   (0) 
    [[0xf7, 0x77, 0x54, 0xff], [0x58, 0x4b, 0x42, 0xff]], # Orange-Brown     (1)
    [[0xf7, 0x77, 0x54, 0xff], [0x22, 0x28, 0x31, 0xff]], # Orange-Darkblue  (2)
    [[0xff, 0xff, 0xff, 0xff], [0x00, 0x00, 0x00, 0xff]], # White-Black      (3)
]

# Index of the color palette to use and draw the FFT spectrum on the screen.
# Above you can get some list of color palettes.
x = 0

fg_color = color_palettes[x][0]
bg_color = color_palettes[x][1]


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
        int(configs['AudioIO']['SampleRate']),
        1, pyaudio.paFloat32,
        input= True,
        stream_callback= _process_audio,
        frames_per_buffer= int(configs['AudioIO']['BufferSize']),
        # NOTE: This feature has been turned off. Because, it lags on WINDOWS.
        # input_device_index= selected_device
    )
except OSError:
    print(red(
        "Encountered problems while intializing Input device(s).",
    )); exit()

from time import sleep
# Start capturing data from the stream.
pcm_stream.start_stream()

# Hook-up this code until input device
# gets disconnected.
while pcm_stream.is_active():
    sleep(LOOKFOR_STREAMCLOSE)

# Close the stream and the interface too.
pcm_stream.stop_stream()
pcm_stream.close()