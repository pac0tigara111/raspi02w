import time
import psutil
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# SPI and Pin Configuration
spi = board.SPI()
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Initialize display
disp = st7789.ST7789(
    spi, cs=cs_pin, dc=dc_pin, rst=reset_pin,
    baudrate=64000000, width=240, height=320,
    x_offset=0, y_offset=0
)

# Create drawing object
image = Image.new("RGB", (disp.width, disp.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

while True:
    # Clear screen with black
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    
    # Get stats
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    
    # Draw text
    draw.text((10, 10), f"CPU: {cpu}%", fill="WHITE")
    draw.text((10, 30), f"RAM: {mem}%", fill="WHITE")
    draw.text((10, 50), time.strftime("%H:%M:%S"), fill="WHITE")
    
    # Display image
    disp.image(image)
    time.sleep(1)
