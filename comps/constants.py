# This Python files contains several constants to make the program dynamic.
# If any variable is changed at here it would affect the entire program.

CONFIG_FILES = [
    "configs/general.yml", # General configuration (e.g samplerate,viewport)
    "configs/colors.yml"   # Colour palettes to draw with.
]
LOOKFOR_STREAMCLOSE = 5 # check in every 5 seconds
NP_FFT_MAXVAL = 255