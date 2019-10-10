# This is the root file of the project.
# If you want to add a feature (use it here).

import pyaudio
from struct import Struct
from visualise import Visualiser
from constants import *
from chalk import red, green
from yaml import safe_load, CLoader
from theme import Theme

components = {
    # Unpacks Float32 data from octets of native-byte order.
    'pcmUnpacker': Struct("=f"),
    'themeLoader': Theme,
    'audioLoader': pyaudio.PyAudio,
    'visualiser': Visualiser
}

# Parses the configuration file corresponding to this program.
# And uses properties of it in several aspects of it.
_configs = safe_load(open(CONFIG_FILES[0]))

# Number of *actually used* bins returned from the Fourier Transform.
# According to Nyquist the samplerate must be the double of the
# frequency. The maximum frequency to reach is 22050 (44100hZ)
_configs['audioIO']['fftBins'] = int(_configs['audioIO']['bufferSize'] / 2)

components['audioLoader'] = pyaudio.PyAudio()
components['visualiser'] = Visualiser(
    _configs['viewport']['width'],
    _configs['viewport']['height'],
    _configs['audioIO']['fftBins']
)


# Maximum number of devices for I/O operation via the Host API.
# TODO: fix the lagging of device selection feature
maximum_device = components['audioLoader'].get_device_count()

# List all the devices supported by the Host API.
# Selection is not avialable due to regressions (would be fixed later).
for device_index in range(maximum_device):
    device_info = components['audioLoader'].get_device_info_by_index(device_index)

    print(
        "[%d %s%s] %s" % (
            device_info['index'],
            green('I') if device_info['maxInputChannels'] else str(),
            red('O') if device_info['maxOutputChannels'] else str(),
            device_info['name']
        )
    )

# Intialize the component theme. And get the color
# palette to draw on the screen.
components['themeLoader'] = Theme(CONFIG_FILES[1])
_theme = components['themeLoader'].getPalette()


def _process_audio(frames, nFrames, timeInfo, status):
    audio_buffer = list(map(
        lambda sample: sample[0],
        components['pcmUnpacker'].iter_unpack(frames)
    ))

    # Draw each buffer recieved from the callback.
    # In the Backend SDL does all the work.
    isClosed = components['visualiser'] \
    .draw(audio_buffer, (
        _theme['background'],
        _theme['foreground']
    ))

    return (bytes(), pyaudio.paComplete) if isClosed \
            else (bytes(), pyaudio.paContinue)

# Open a full-duplex stream which can output and input.
# We pipe input to output. And visuailse the Input as FFT spectrum.
try:
    pcm_stream = components['audioLoader'].open(
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

# Hook-up this application theread to the PortAudio thread.
# And, wait until the PortAudio thread exits.
while pcm_stream.is_active():
    sleep(LOOKFOR_STREAMCLOSE)

pcm_stream.stop_stream()
pcm_stream.close()
