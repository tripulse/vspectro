import pyaudio
from struct          import Struct
from comps.visualise import Visualiser
from comps.constants import *
from comps.palettes  import PaletteContext
from yaml            import load, CLoader
from visuals.fftspec import FFTSpectrum
from utils           import SDL_IsEventOccured
from sdl2            import SDL_QUIT

class Spectro():
    config = {}
    components = {}

    def __init__(self, configuration: dict = None):
        self.config = configuration
        self.components = {
            'audio':        pyaudio.PyAudio(), #< audio backend to recieve audio data
            'theming':      PaletteContext(),
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

        # Parse the configuration from the correspoding configuration file
        # and store that into the class for later rendering.
        self.components['theming'].parse(open(ConfigFiles['palette']).read())

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

    def audiodevices(self) -> dict:
        """
        Provides an iterator over all the devices that can be accessed by PyAudio API.
        This adds an abstraction over 'for looping' all the devices are avialable via
        the Host Audio API.

        :rtype dict:
            Information about each device's charecteristics.
        """

        for devidx in range(self.components['audio'].get_device_count()):
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

        # Return the samples for Playback of audio. With status, ok.
        #       frames in octets  reponse of callback
        return (     frames,      pyaudio.paContinue)

    def close(self):
        raise NotImplementedError("The close function is not implemented yet!")

import comps.configloader as configloader
import logging
import sys
import tkinter
import gui.info

gui_main = tkinter.Tk()

""" Configure the logging system. All the logs would be 
    dumped into the STDOUT. """
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
root_logger.addHandler(stdout_handler)

def main():
    # Load the general config from the config file. The documentation is
    # on the https://github.com/nullvideo/spectro/wiki.
    main_config = configloader.ConfigContext(configloader.ConfigType.Yaml)
    main_config.parse(open(ConfigFiles['general']).read())

    # Add a GUI interface to the program. If the GUI closes the 
    # entire application itself does close.
    gui.info.Information(gui_main) \
        .display_info(main_config.parsed_config)
    
    # Specify the amount of FFT bins we require to show in the window.
    main_config.parsed_config['n_fftbins'] = \
        int(main_config.parsed_config['audioIO']['bufferSize'] / 2)

    main_app = Spectro(main_config.parsed_config)
    root_logger.info(f"Intialised the application instance {main_app.__repr__()}")

    gui_main.title("Signal Properties")

    # Listing of Audio IO devices whose are avialable
    # via the Host API. Selected devices would be highlighted.
    (indev_id, outdev_id) = (main_app.components['audio']
                            .get_default_input_device_info()['index'],
                             main_app.components['audio']
                            .get_default_output_device_info()['index'])

    root_logger.info("List of Input and Output devices:")
    for index, device in enumerate(main_app.audiodevices()):
        if index in (indev_id, outdev_id):
            root_logger.info(" [%s*] %s" % (index, device['name']))
        else:
            root_logger.info(" [%s] %s" % (index, device['name']))

    gui_main.mainloop()


if __name__ == "__main__":
    main()