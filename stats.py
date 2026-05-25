import time
import psutil
import socket
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# --- Configuration ---
spi = board.SPI()
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

disp = st7789.ST7789(
    spi, cs=cs_pin, dc=dc_pin, rst=reset_pin,
    baudrate=64000000, width=240, height=320,
    x_offset=0, y_offset=0
)

# Load fonts
try:
    font_main = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except:
    font_main = ImageFont.load_default()
    font_small = ImageFont.load_default()

def get_color(percent):
    """Returns a color based on usage intensity."""
    if percent > 80: return "RED"
    if percent > 50: return "YELLOW"
    return "LIME"

def draw_bar(draw, x, y, width, height, percent, color):
    # Background bar
    draw.rectangle((x, y, x + width, y + height), outline="WHITE", fill="#222222")
    # Foreground fill
    fill_width = (width * percent) / 100
    draw.rectangle((x, y, x + fill_width, y + height), fill=color)

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "Offline"

image = Image.new("RGB", (disp.width, disp.height))
draw = ImageDraw.Draw(image)

while True:
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temp = psutil.sensors_temperatures()['cpu_thermal'][0].current
    ip = get_ip()

    # Clear screen
    draw.rectangle((0, 0, disp.width, disp.height), fill="BLACK")

    # Header with a subtle decorative element
    draw.text((10, 10), "SYSTEM DASHBOARD", font=font_main, fill="WHITE")
    draw.ellipse((210, 10, 225, 25), fill="LIME" if cpu < 80 else "RED") # Status "Light"

    # Metrics
    y = 60
    for label, val in [("CPU", cpu), ("RAM", mem), ("DSK", disk)]:
        draw.text((10, y), label, font=font_main, fill="WHITE")
        draw_bar(draw, 60, y + 2, 160, 16, val, get_color(val))
        y += 50

    # Footer section
    draw.line((10, 210, 230, 210), fill="#444444")
    draw.text((10, 230), f"TEMP: {temp:.1f} C", font=font_main, fill="CYAN")
    draw.text((10, 265), f"IP: {ip}", font=font_small, fill="WHITE")
    draw.text((10, 290), f"{time.strftime('%a, %d %b %H:%M')}", font=font_small, fill="GREY")

    disp.image(image)
    time.sleep(1)
