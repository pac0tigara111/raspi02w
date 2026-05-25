import board
import digitalio
from adafruit_rgb_display import st7789

# Configure SPI
spi = board.SPI()
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Initialize display
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=64000000,
    width=240,
    height=320,
    x_offset=0,
    y_offset=0,
)

# Create a test image
from PIL import Image
img = Image.new("RGB", (240, 320), "red")
disp.image(img)
