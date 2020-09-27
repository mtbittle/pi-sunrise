import configparser
import time
import cec
from rpi_ws281x import *

# LED strip configuration:
LED_COUNT      = 15      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def readconfig():

    print("Reading configuration file to determine if values exist.")
    config = configparser.ConfigParser()
    config.read('appconfig.ini')
    print(config.sections())
    return config


def get_from_config(section, property_key):
    return configurer.get(section, property_key)


# Main program logic follows:
if __name__ == '__main__':
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    #init the cec controller for tv
    cec.init()
    tv = cec.Device(cec.CECDEVICE_TV)

    # read config and get dawn/dusk times
    configurer = readconfig()
    dawn_time_str = get_from_config('Dusk Till Dawn', 'dawn_time')
    dusk_time_str = get_from_config('Dusk Till Dawn', 'dusk_time')
    print('dawn: ' + dawn_time_str + ', dusk: ' + dusk_time_str)

    # convert the string values to times so we can compare to current time
    dawn_t = time.strptime('%H:%M:%S', dawn_time_str)
    dusk_t = time.strptime('%H:%M:%S', dusk_time_str)
    localtime = time.localtime()
    if localtime >= dawn_t and localtime < dusk_t:
        if tv.is_on():
            colorWipe(strip, Color(0,0,0), 10)
    else:
        if tv.is_on():
            colorWipe(strip, Color(0,0,0), 10)
        else:
            colorWipe(strip, Color(0, 255, 0))
