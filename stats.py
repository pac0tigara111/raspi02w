import time
import psutil
from PIL import Image, ImageDraw, ImageFont
import ST7789 # Assuming you have the Waveshare library files in your folder

# Initialize display (using the Waveshare driver methods)
disp = ST7789.ST7789(port=0, cs=0, dc=25, backlight=23, rst=24)
disp.begin()

width = disp.width
height = disp.height
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

# Load a font (You can use default or point to a .ttf file)
font = ImageFont.load_default()

while True:
    # Get stats
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    
    # Clear screen
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    # Draw text
    draw.text((10, 10), f"CPU Usage: {cpu}%", font=font, fill="WHITE")
    draw.text((10, 30), f"Memory: {mem}%", font=font, fill="WHITE")
    draw.text((10, 50), time.strftime("%H:%M:%S"), font=font, fill="WHITE")
    
    # Display to screen
    disp.display(image)
    time.sleep(1)
