import time
import psutil
import socket
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
# If your screen is upside down or mirrored, try rotation=90 or rotation=270
disp = st7789.ST7789(
    spi, cs=cs_pin, dc=dc_pin, rst=reset_pin,
    baudrate=64000000, width=240, height=320,
    x_offset=0, y_offset=0
)

# Load a larger font
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
except:
    font = ImageFont.load_default()

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No Network"

# Create drawing object
image = Image.new("RGB", (disp.width, disp.height))
draw = ImageDraw.Draw(image)

while True:
    # Get stats
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    temp = psutil.sensors_temperatures()['cpu_thermal'][0].current
    disk = psutil.disk_usage('/').percent
    ip = get_ip()
    
    # Clear screen
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    
    # Text data
    stats = [
        (f"CPU: {cpu}%", "WHITE"),
        (f"RAM: {mem}%", "WHITE"),
        (f"TEMP: {temp:.1f}C", "YELLOW"),
        (f"DISK: {disk}%", "GREEN"),
        (f"IP: {ip}", "CYAN")
    ]
    
    # Draw centered text
    y = 20
    for text, color in stats:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((disp.width - w) / 2, y), text, font=font, fill=color)
        y += 50
    
    # Display image
    disp.image(image)
    time.sleep(2)
