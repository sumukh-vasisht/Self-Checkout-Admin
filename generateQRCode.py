import pyqrcode 
import png 
from pyqrcode import QRCode 
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol

s = "guest2"

url = pyqrcode.create(s)

url.svg("myqr.svg", scale = 8) 

url.png('myqr.png', scale = 6) 

img = cv2.imread('myqr.png', cv2.IMREAD_GRAYSCALE)
codes = decode(img)
print('DECODED', codes[0][0].decode("utf-8"))