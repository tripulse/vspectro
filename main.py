import pyaudio
from struct          import Struct
from comps.visualise import Visualiser
from comps.constants import *
from comps.theme     import Theme
from yaml            import load, CLoader
from visuals.fftspec import FFTSpectrum
from utils           import SDL_IsEventOccured
from sdl2            import SDL_QUIT

class Spectro():
    config = {}
    components = {}

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
            'visualiser_cb': FFTSpectrum(      #< the visualiser callback (renders itself into datapoints)
                self.config['audioIO']['bufferSize'],
                self.config['viewport']['width']
            )
        }

        # Palette Index is specifed in the configuration file.
        # So, don't mess with Indices of Palette.
        color_palette = self.components['theming'] \
                            .getPalette()

        # The callback function which is called to return data
        # the paint() method is invoked.
        self.components['visualiser'] \
            .set_callback(self.components['visualiser_cb'].compute)

        self.components['visualiser'] \
            .set_palette(
                color_palette['foreground'],
                color_palette['background']
            )

        # Opens a stream to recieve or send the Audio data.
        # NOTE: always mono because we don't want to implement
        #       stereo input, float32 because it is easier to
        #       work with and requires no scaling when passed
        #       for FFT computation, non-blocking I/O because
        #       blocking method is inefficient in this case
        audio_stream = self.components['audio'].open(
            self.config['audioIO']['sampleRate'],
            1, pyaudio.paFloat32,
            input= True,
            output= True,
            stream_callback= self._process_audiodata,
            frames_per_buffer= self.config['audioIO']['bufferSize']
        )

        self.components['audio_stream'] = audio_stream
        audio_stream.start_stream()

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
                self.components['audio']\
                    .get_device_info_by_index(devidx)

    def _process_audiodata(
        self, 
        frames, nFrames, 
        timeInfo, status
    ) -> tuple:
        """
        This method is a internal method to process, visualise, playback
        audio recieved from the input.
        """
        audiobuffer = tuple(map(
            lambda sample: sample[0],
            self.components['pcm_unpacker'] \
                .iter_unpack(frames)
        ))

        self.components['visualiser'] \
            .paint(audiobuffer, self.config['viewport']['height'])

        # CONDITION: if window has encountered a close event
        # then close everything.
        if SDL_IsEventOccured(SDL_QUIT):
            print(
                "The application has encountered a close event"
                "; closing everything."
            )

            self.close()
            return (frames, pyaudio.paComplete)

        # Return the samples for Playback of audio. With status, ok.
        #       frames in octets  reponse of callback
        return (     frames,      pyaudio.paContinue)

    def close(self):
        raise NotImplementedError("The close function is not implemented yet!")

def main():
    with open('configs/general.yml', 'r') as config_file:
        config = load(config_file, Loader=CLoader)
        config['audioIO']['nfft_bins'] = int(
            config['audioIO']['bufferSize']
            / 2
        )

        # The instance of the class also known as the
        # main application.
        _app = Spectro(config)

    # Listing of Audio IO devices whose are avialable
    # via the Host API. Selected devices would be highlighted.
    (indev_id, outdev_id) = (_app.components['audio']
                            .get_default_input_device_info()['index'],
                             _app.components['audio']
                            .get_default_output_device_info()['index']
                            )

    print("List of IO devices:")
    for index, device in enumerate(_app.list_audiodevices()):
        if index in (indev_id, outdev_id):
            print(" [%s*] %s" % (index, device['name']))
        else:
            print(" [%s] %s" % (index, device['name']))


    # Legacy thread-hooking. Idk, what I'm doing here.
    # TODO: implement multi-threading and hook up PortAudio thread
    #       with the main thread.
    import time
    while _app.components['audio_stream'].is_active():
        time.sleep(LOOKFOR_STREAMCLOSE)

if __name__ == "__main__":
    main()