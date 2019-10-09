from yaml import load, CLoader


# class<Theme>: loads all the color palettes from a file,
#               it returns the pallete (based on index) from the file.
class Theme():
    def __init__(self, filename: str):
        file_contents = open(filename, "rb").read()
        self._config = load(file_contents, Loader=CLoader)
    
    def getPalette(self):
        index    = self._config['paletteIndex']
        palettes = self._config['palettes']

        return ({
            'foreground': palettes[index][0],
            'background': palettes[index][1]
        })