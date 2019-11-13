from pyaudio         import PyAudio, paContinue, paFloat32
from struct          import Struct
from comps.visualise import Visualiser
from comps.constants import *
from comps.palettes  import PaletteContext
from visuals.fftspec import FFTSpectrum, PlotDimensions
from utils           import SDL_IsEventOccured
from sdl2            import SDL_QUIT
from comps.comploader import ComponentContext
from operator        import itemgetter 

# An instance of the component manger for the root program.
root_components = ComponentContext()

class Spectro():
    config = {}

    def __init__(self, config: dict = None):
        self.config = config

        """ Register all the components required to execute. """
        root_components.register('portaudio', PyAudio())
        root_components.register('palette_manager', PaletteContext())
        root_components.register('pcm_byteunpacker', Struct('f'))
        root_components.register('visualizer', Visualiser(self.__repr__(), 
            config['viewport']['width'], config['viewport']['height']
        ))
    
    def init(self):
        palettes   = root_components.access('palette_manager')
        visualiser = root_components.access('visualizer')

        palettes.parse(open(ConfigFiles['palette']).read())
        logging.debug("Parsed the colourpalette.")

        # The callback function which is called to return data
        # the paint() method is invoked.
        visualiser \
        .set_callback(FFTSpectrum(
            self.config['audioIO']['bufferSize'],
            self.config['viewport']['width'],
            PlotDimensions(
                self.config['viewport']['width'],
                self.config['viewport']['height']
            )
        ).compute)

        visualiser \
        .set_palette(
            *itemgetter('foreground', 'background') \
            (palettes.getPalette())
        )

        root_components.access('portaudio').open(
            self.config['audioIO']['sampleRate'],
            1, paFloat32,
            input= True,
            output= True,
            stream_callback= self._process_audiodata,
            frames_per_buffer= self.config['audioIO']['bufferSize']
        ).start_stream()

    def audiodevices(self) -> dict:
        """
        Provides an iterator over all the devices that can be accessed by PyAudio API.
        This adds an abstraction over 'for looping' all the devices are avialable via
        the Host Audio API.

        :rtype dict:
            Information about each device's charecteristics.
        """
        pa = root_components.access('portaudio')

        for devidx in range(pa.get_device_count()):
            yield pa.get_device_info_by_index(devidx)

    def _process_audiodata(
        self, 
        frames, nFrames,
        timeInfo, status
    ) -> tuple:
        """
        This method is a internal method to process, visualise, playback
        audio recieved from the input.
        """

        root_components.access('visualizer').paint(map(
            lambda sample: sample[0],
            root_components.access('pcm_byteunpacker') \
                .iter_unpack(frames)
        ))

        # Return the samples for Playback of audio. With status, ok.
        #       frames in octets  reponse of callback
        return (     frames,      paContinue)

    def close(self):
        raise NotImplementedError("The close function is not implemented yet!")

import comps.configloader as configloader
import logging
import sys
import tkinter
import gui.objview

gui_main = tkinter.Tk()
gui_main.title("Configuration Explorer")

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

    main_app = Spectro(main_config.parsed_config); main_app.init()
    root_logger.info(f"Intialised the application instance {main_app.__repr__()}")

    logging.debug(root_components.access('palette_manager').parsed_config)

    gui.objview.ObjectViewer(gui_main, main_config.parsed_config)
    gui.objview.ObjectViewer(gui_main, root_components.access('palette_manager').parsed_config)

    pa = root_components.access('portaudio')
    # Listing of Audio IO devices whose are avialable
    # via the Host API. Selected devices would be highlighted.
    (indev_id, outdev_id) = (pa.get_default_input_device_info()['index'],
                             pa.get_default_output_device_info()['index'])

    root_logger.info("List of Input and Output devices:")
    for index, device in enumerate(main_app.audiodevices()):
        if index in (indev_id, outdev_id):
            root_logger.info(" [%s*] %s" % (index, device['name']))
        else:
            root_logger.info(" [%s] %s" % (index, device['name']))

    gui_main.mainloop()


if __name__ == "__main__":
    main()