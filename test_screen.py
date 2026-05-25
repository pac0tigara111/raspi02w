import st7789
from PIL import Image, ImageDraw
import board
import digitalio

# Simple initialization test
# You may need to adjust these pins to match your actual wiring
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
BAUDRATE = 64000000

disp = st7789.ST7789(
    board.SPI(),
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Fill with red to prove it's working
img = Image.new("RGB", (240, 320), "red")
disp.image(img)
