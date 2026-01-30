#SERVICE_NAME = "ABS01" 
from PIL.ImageFont import ImageFont
import psutil
import ctypes
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import time
import os
import win32api
import win32gui
import win32ui
import win32con

SERVICE_NAME = "ABS01"
 


def get_service_status(service_name):
    """Checks if the Flask service is running."""
    try:
        service = psutil.win_service_get(service_name)
        if service.status() == 'running':
            return True
    except Exception as e:
        print(f"Error fetching service status: {e}")
    return False


def extract_icon_from_exe(exe_path):
    """Extracts an icon from an EXE using pywin32."""
    try:
        large, small = win32gui.ExtractIconEx(exe_path, 0, 1)
        hicon = large[0] if large else small[0]
        # Get icon dimensions
        width, height = 16 , 32  # Default icon size

        # Create a device context to hold the icon
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, width, height)

        hdc_mem = hdc.CreateCompatibleDC()
        hdc_mem.SelectObject(hbmp)

        # Draw the icon to the bitmap
        win32gui.DrawIcon(hdc_mem.GetHandleOutput(), 0, 0, hicon)

        # Convert bitmap to image
        bmp_info = hbmp.GetInfo()
        bmp_str = hbmp.GetBitmapBits(True)
        image = Image.frombuffer('RGBA', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, 'raw', 'BGRA', 0, 1)
         
        
        # Cleanup
        win32gui.DestroyIcon(hicon)

        return image

    except Exception as e:
        print(f"Failed to extract icon from EXE: {e}")
        return Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))  # Return a default icon on failure


def update_menu(icon):
    """Continuously updates the system tray menu with Flask service status."""
    while True:
        status = get_service_status(SERVICE_NAME)
        status_text = "Running" if status else "Stopped"

        # Update the tray menu with the new status
        icon.menu = Menu(
            MenuItem(f"Serviceq Status: {status_text}", None, enabled=False),
            MenuItem(f"Service Status: {status_text}", None, enabled=False),
            MenuItem("Quit", quit_app)
        )
        time.sleep(5)  # Check status every 5 seconds



def quit_app(icon, item):
    """Exits the system tray application."""
    icon.stop()


def get_service_exe_path(service_name):
    """Retrieve the executable path of the service."""
    try:
        service = psutil.win_service_get(service_name)
        config = service.as_dict()
        return config.get("binpath", "").replace('"', '')  # Clean up any quotes in the path
    except Exception as e:
        print(f"Error getting service executable path: {e}")
        return None


def setup_tray():
    """Initializes the system tray icon and menu with Flask server status."""
    
    # Get the path of the service executable
    exe_path = get_service_exe_path(SERVICE_NAME)
    exe_path = "C:\\Program Files (x86)\\ApnaBackup Server\\abc.exe"

    if exe_path and os.path.exists(exe_path):
        # Extract the icon from the service's executable
        image = extract_icon_from_exe(exe_path)
        image = Image.open("C:\\Users\\user\\Documents\\IPMsg\\AutoSave\\Client.png")

    else:
        # Use a placeholder icon if the service exe path is not available
        image = Image.new('RGBA', (128, 32), color=(2, 2, 30, 60))
    draw = ImageDraw.Draw(image)
    #draw.rectangle((0, 0, 10, 10), fill=(255, 0, 0, 255))  # White background
    #draw.text((10, 10), "My Icon", fill=(30, 80, 130))  # Black text
    for x in range(32):
        for y in range(32):
            # Check if the pixel is white
            #if image.getpixel((x, y)) == (255, 255, 255, 255):
            if image.getpixel((x, y)) != (255, 0, 0, 0)and image.getpixel((x, y)) != (0, 0, 0, 0):
                image.putpixel((x, y), (0, 0, 255, 0))
    # Create the tray icon
    iconx = Icon("Apna Backup Service Monitor", image)
    # Start a separate thread to update the status in the tray menu
    t1= threading.Thread(target=update_menu, args=(iconx,), daemon=True)
    #iconx.run()
    # for x in range(16):
    #     for y in range(16):
    #         # Check if the pixel is white
    #         if image.getpixel((x, y)) == (255, 255, 255, 255):
    #             image.putpixel((x, y), (0,0, 200, 255))
    i1=Image.new('RGBA', (128, 32), color=(2, 2, 30, 255))
    i1 = Image.open("C:\\Users\\user\\Documents\\IPMsg\\AutoSave\\Server.png")

    draw = ImageDraw.Draw(i1)
    draw.text((10, 10), " Apna  B ",stroke_width=5, fill=(255,255, 255))  # Black text
    
    icon = Icon("Apna Backup Service Monitor", i1)
    # Start a separate thread to update the status in the tray menu
    t2=threading.Thread(target=update_menu, args=(icon,), daemon=True)
    t3=threading.Thread(target=iconx.run,   daemon=True)
    t4= threading.Thread(target=icon.run,  daemon=True)

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    #icon.run()

    # Run the tray icon


if __name__ == "__main__":
    setup_tray()

# import psutil
# import threading
# from pystray import Icon, MenuItem, Menu
# from PIL import Image, ImageDraw
# import time

# # Define the name of the service running your Flask server
# SERVICE_NAME = "SQLBrowser"

# def create_image(status):
#     """Creates an image for the system tray icon.
    
#     The icon is green if the Flask service is running, red if stopped.
#     """
#     width = 64
#     height = 64
#     image = Image.new('RGB', (width, height), (255, 255, 255))
#     draw = ImageDraw.Draw(image)
    
#     # Green for running, Red for stopped
#     color = (0, 255, 0) if status else (255, 0, 0)
#     draw.rectangle((0, 0, width, height), fill=color)
#     return image

# def get_service_status(service_name):
#     """Checks if the Flask service is running.
    
#     Returns True if running, False otherwise.
#     """
#     try:
#         service = psutil.win_service_get(service_name)
#         if service.status() == 'running':
#             return True
#     except Exception as e:
#         print(f"Error fetching service status: {e}")
#     return False

# def update_icon(icon):
#     """Continuously updates the system tray icon based on Flask service status."""
#     while True:
#         status = get_service_status(SERVICE_NAME)
#         icon.icon = create_image(status)
#         time.sleep(5)  # Check status every 5 seconds

# def quit_app(icon, item):
#     """Exits the system tray application."""
#     icon.stop()

# def setup_tray():
#     """Initializes the system tray icon and menu."""
#     icon = Icon("Flask Service Monitor")
    
#     # Define the tray menu with only a "Quit" option
#     icon.menu = Menu(
#         MenuItem("Quit", quit_app)
#         MenuItem("About ApnaBackup","")
#     )
    
#     # Start a separate thread to keep updating the icon
#     threading.Thread(target=update_icon, args=(icon,), daemon=True).start()
    
#     # Run the tray icon
#     icon.run()

# if __name__ == "__main__":
#     setup_tray()


