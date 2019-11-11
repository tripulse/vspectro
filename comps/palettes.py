from .configloader import ConfigContext, ConfigType
import logging

class PaletteContext(ConfigContext):
    def __init__(self):
        super().__init__(ConfigType.Yaml)
    
    def getPalette(self, index: int = None):
        if type(index) == int:
            palette_index = index
        elif not index:
            try:
                palette_index = self.parsed_config['paletteIndex']
            except AttributeError:
                logging.exception("Palette index hasn't been found neither one provided!")

        logging.debug(f"Requested palette at (index= {palette_index})")

        try:
            palettes = self.parsed_config['palettes']
            logging.debug(f"Found palettes: {palettes}")
        except AttributeError:
            logging.exception("Entry of palettes hasn't been found!")

        try:
            (_fg, _bg) = (palettes[palette_index][0], palettes[palette_index][1])
            return {
                'foreground': (_fg >> 24, _fg >> 16 & 0xff, _fg >> 8 & 0xff, _fg & 0xff),
                'background': (_bg >> 24, _bg >> 16 & 0xff, _bg >> 8 & 0xff, _bg & 0xff)
            }
        except IndexError:
            logging.exception(f"Palette at (index= {palette_index}) hasn't been found")