import time
import os
import psutil
import socket
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# --- Hardware Configuration ---
spi = board.SPI()
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

disp = st7789.ST7789(
    spi, cs=cs_pin, dc=dc_pin, rst=reset_pin,
    baudrate=64000000, width=240, height=320,
    x_offset=0, y_offset=0
)

# --- Font Setup ---
try:
    font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    font_md = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except:
    font_lg = font_md = font_sm = ImageFont.load_default()

# --- Helpers ---
def get_color(percent):
    if percent > 85: return "#FF3333" # Bright Red
    if percent > 60: return "#FFD700" # Gold/Yellow
    return "#00FF66" # Neon Green

def format_bytes(bytes_val):
    if bytes_val < 1024: return f"{bytes_val:.0f} B"
    elif bytes_val < 1048576: return f"{bytes_val/1024:.1f} KB"
    else: return f"{bytes_val/1048576:.1f} MB"

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "Offline"

def draw_sparkline(draw, x, y, w, h, data_list, color):
    """Draws a mini line graph for historical data."""
    draw.rectangle((x, y, x+w, y+h), outline="#333333", fill="#111111")
    if len(data_list) < 2: return
    
    # Map data points to X, Y coordinates
    points = []
    x_step = w / (len(data_list) - 1)
    for i, val in enumerate(data_list):
        px = x + (i * x_step)
        py = y + h - ((val / 100.0) * h)
        points.append((px, py))
    
    draw.line(points, fill=color, width=2)

def draw_bar(draw, x, y, w, h, percent, color):
    """Draws a standard progress bar."""
    draw.rectangle((x, y, x+w, y+h), outline="#444444", fill="#222222")
    fill_w = (w * percent) / 100
    draw.rectangle((x, y, x+fill_w, y+h), fill=color)

# --- State Variables ---
cpu_history = [0] * 50  # Keep last 50 CPU readings for the graph
last_net = psutil.net_io_counters()
last_time = time.time()
boot_time = psutil.boot_time()

# Create canvas
image = Image.new("RGB", (disp.width, disp.height))
draw = ImageDraw.Draw(image)

# --- Main Loop ---
while True:
    current_time = time.time()
    dt = current_time - last_time
    if dt == 0: dt = 1 # Prevent divide by zero
    
    # 1. Fetch System Stats
    cpu = psutil.cpu_percent()
    cpu_history.append(cpu)
    cpu_history.pop(0) # Keep list at exactly 50 items
    
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    temp = psutil.sensors_temperatures().get('cpu_thermal', [{'current': 0}])[0].current
    load_avg = os.getloadavg()
    
    # Uptime math
    uptime_sec = current_time - boot_time
    uptime_str = f"{int(uptime_sec//3600)}h {int((uptime_sec%3600)//60)}m"
    
    # Network math
    net = psutil.net_io_counters()
    tx_speed = (net.bytes_sent - last_net.bytes_sent) / dt
    rx_speed = (net.bytes_recv - last_net.bytes_recv) / dt
    last_net = net
    last_time = current_time

    # 2. Draw Background
    draw.rectangle((0, 0, disp.width, disp.height), fill="#0A0A0A") # Very dark grey

    # 3. Header
    draw.text((10, 5), "ZERO 2 W DASH", font=font_md, fill="#FFFFFF")
    draw.text((165, 8), f"UP: {uptime_str}", font=font_sm, fill="#AAAAAA")
    draw.line((10, 25, 230, 25), fill="#444444")

    # 4. CPU Section (Graph + Text)
    draw.text((10, 35), "CPU Load", font=font_sm, fill="#CCCCCC")
    draw.text((170, 30), f"{cpu}%", font=font_lg, fill=get_color(cpu))
    draw_sparkline(draw, 10, 55, 220, 35, cpu_history, get_color(cpu))
    
    # Load averages under graph
    draw.text((10, 95), f"Load Avg: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}", font=font_sm, fill="#888888")

    # 5. Memory & Disk Bars
    draw.text((10, 125), "RAM", font=font_sm, fill="#FFFFFF")
    draw.text((180, 125), f"{mem.percent}%", font=font_sm, fill=get_color(mem.percent))
    draw_bar(draw, 10, 140, 220, 12, mem.percent, "#00CCFF") # Cyan

    draw.text((10, 165), "DISK", font=font_sm, fill="#FFFFFF")
    draw.text((180, 165), f"{disk.percent}%", font=font_sm, fill=get_color(disk.percent))
    draw_bar(draw, 10, 180, 220, 12, disk.percent, "#FF00FF") # Magenta

    # 6. Network Section (with drawn arrows)
    draw.line((10, 205, 230, 205), fill="#444444")
    
    # Draw Down Arrow (RX)
    draw.polygon([(15, 215), (25, 215), (20, 222)], fill="#00FF66")
    draw.text((30, 212), f"DL: {format_bytes(rx_speed)}/s", font=font_sm, fill="#FFFFFF")
    
    # Draw Up Arrow (TX)
    draw.polygon([(135, 222), (145, 222), (140, 215)], fill="#FFD700")
    draw.text((150, 212), f"UL: {format_bytes(tx_speed)}/s", font=font_sm, fill="#FFFFFF")

    # 7. Footer (2-Column Grid)
    draw.line((10, 240, 230, 240), fill="#444444")
    
    # Column 1 (Left)
    draw.text((10, 250), "TEMP", font=font_sm, fill="#888888")
    draw.text((10, 265), f"{temp:.1f}°C", font=font_lg, fill=get_color(temp))

    # Column 2 (Right)
    draw.text((130, 250), "IP ADDRESS", font=font_sm, fill="#888888")
    draw.text((130, 265), get_ip(), font=font_md, fill="#00CCFF")
    
    # Clock at the very bottom right
    draw.text((180, 300), time.strftime('%H:%M:%S'), font=font_sm, fill="#666666")

    # 8. Push to Display
    disp.image(image)
    
    # Sleep is reduced slightly for a smoother graph update
    time.sleep(0.5)
