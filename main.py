# This is the root file of the project.
# If you want to add a feature (use it here).

import pyaudio
from sdl2            import SDL_PollEvent, SDL_QUIT
from struct          import Struct
from comps.visualise import Visualiser
from comps.constants import *
from comps.theme     import Theme
from yaml            import load, CLoader
from visuals.fftspec import FFTSpectrum

class Spectro():
    # Short description about the class itself.
    def __repr__(self):
        return "Spectro — a spectrum analyser in Python"

    def __init__(self, configuration: dict = None):
        self.config = configuration
        self.components = {
            'audio':        pyaudio.PyAudio(), #< audio backend to recieve audio data
            'theming':      Theme(             #< theme manager of the program
                CONFIG_FILES[1]
            ),
            'pcm_unpacker': Struct('=f'),      #< unpacks float32 data in native byte order,
            'visualiser':   Visualiser(        #< visualizes datapoints (usually samples or frequnecy bins),
                self.__repr__(),
                self.config['viewport']['width'],
                self.config['viewport']['height'],
            ),
            'visualiser_cb': FFTSpectrum(
                self.config['audioIO']['bufferSize'],
                self.config['viewport']['width']
            )
        }

        color_palette = self.components['theming'] \
                            .getPalette()

        self.components['visualiser'] \
            .set_callback(self.components['visualiser_cb'].compute)

        self.components['visualiser'] \
            .set_palette(
                color_palette['foreground'],
                color_palette['background']
            )

        audioStream = self.components['audio'].open(
            self.config['audioIO']['sampleRate'],
            1, pyaudio.paFloat32,
            input= True,
            stream_callback= self.process_audiodata,
            frames_per_buffer= self.config['audioIO']['bufferSize']
        )

        # Register as a component of the class.
        # Can be used by other methods later on.
        self.components['audio_stream'] = audioStream

        # Start the audio stream recieve data from the input audio
        # device show spectrum on the Visualiser.
        audioStream.start_stream()

    def list_audiodevices(self) -> dict:
        """Iterates find the devices that can be accessed by PortAudio API.
        The function runs an iteration process and looks up all the input/output
        devices and returns information about each device in a dictionary.

        :rtype dict:
            Each dictionary conatins information about the device.
        """

        # Maximum number of devices provided by the Host API of
        # the operating system. Used for iteration of devices.
        max_devices = self.components['audio'].get_device_count()

        # Loops trough all the devices and returns signle output
        # device per call (basically, implementing an iterator).
        for devidx in range(max_devices):
            yield \
                self.components['audio'].get_device_info_by_index(devidx)

    def process_audiodata(
        self, 
        frames, nFrames, 
        timeInfo, status
    ) -> tuple:
        audiobuffer = tuple(map(
            lambda sample: sample[0],
            self.components['pcm_unpacker'] \
                .iter_unpack(frames)
        ))

        self.components['visualiser'] \
            .paint(audiobuffer,
                self.config['viewport']['height']
            )

        if SDL_QUIT == SDL_PollEvent(
            self.components['visualiser'] 
                .context['events']
        ):
            return (bytes(), pyaudio.paComplete)
        
        # Continue until SDL_QUIT event occurs.
        return (bytes(), pyaudio.paContinue)

    def close(self):
        pass

def main():
    config = load(open('configs/general.yml', 'r'), Loader=CLoader)
    config['audioIO']['nfft_bins'] = int(config['audioIO']['bufferSize']/2)

    spectro = Spectro(config)

    # Lists audio devices that avialable via
    # the Host API.
    for index, device in enumerate(spectro.list_audiodevices()):
        print("[%d] %s" % (index, device['name']))

    import time
    while spectro.components['audio_stream'].is_active():
        time.sleep(LOOKFOR_STREAMCLOSE)

if __name__ == "__main__":
    main()