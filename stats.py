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

def draw_bar(draw, x, y, width, height, percent, color):
    # Background bar (grey)
    draw.rectangle((x, y, x + width, y + height), outline="WHITE", fill="#333333")
    # Foreground fill (colored)
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
    # Get stats
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temp = psutil.sensors_temperatures()['cpu_thermal'][0].current
    ip = get_ip()

    # Clear screen (dark background)
    draw.rectangle((0, 0, disp.width, disp.height), fill="BLACK")

    # Draw Header
    draw.text((10, 10), "PI ZERO 2 W MONITOR", font=font_main, fill="WHITE")
    draw.line((0, 40, 240, 40), fill="WHITE")

    # Draw Metrics with bars
    y = 60
    metrics = [
        ("CPU", cpu, "RED"),
        ("RAM", mem, "BLUE"),
        ("DISK", disk, "GREEN")
    ]

    for label, val, color in metrics:
        draw.text((10, y), f"{label}: {val}%", font=font_main, fill="WHITE")
        draw_bar(draw, 80, y + 5, 140, 15, val, color)
        y += 50

    # Draw Bottom Info
    draw.text((10, 220), f"TEMP: {temp:.1f} C", font=font_main, fill="YELLOW")
    draw.text((10, 260), f"IP: {ip}", font=font_small, fill="CYAN")
    draw.text((10, 290), f"TIME: {time.strftime('%H:%M:%S')}", font=font_small, fill="WHITE")

    # Display to screen
    disp.image(image)
    time.sleep(1)
