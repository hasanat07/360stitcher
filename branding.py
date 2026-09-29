from pathlib import Path
from PIL import Image, ImageTk

NAME = '360 Stitcher'
CREDIT = 'Developed by Ahmad Alhasanat'
ASSETS = Path(__file__).resolve().parent / 'assets'

def set_icon(window):
    with Image.open(ASSETS / 'logo.jpg') as source:
        icon=source.copy()
        icon.thumbnail((128,128),Image.Resampling.LANCZOS)
    window._brand_icon=ImageTk.PhotoImage(icon)
    window.iconphoto(False,window._brand_icon)
