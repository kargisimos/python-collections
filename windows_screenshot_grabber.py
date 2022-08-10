#this script takes a screenshot of the user's desktop
#and saves it as <username>_<hostname>_<timestamp>.jpg

from PIL import ImageGrab
from socket import gethostname
from getpass import getuser
from datetime import datetime

def windows_screenshot_grabber():
    filename = f'{getuser()}_{gethostname()}_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.jpg'
    ImageGrab.grab().save(filename,'JPEG')

windows_screenshot_grabber()
