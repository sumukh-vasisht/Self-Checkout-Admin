import tkinter as tk
from tkinter import Label
import pyqrcode 
import png 
from pyqrcode import QRCode 
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import ImageTk, Image

s = "guest2"
url = pyqrcode.create(s)
# url.svg("myqr.svg", scale = 8) 
url.png('myqr.png', scale = 6)

thankYouPage=tk.Tk()
thankYouPage.title("ABC Mart")
thankYouPage.geometry("500x500+300-100")
title=Label(thankYouPage,text="BILL DETAILS", font=('comicsana',18)).place(x=170,y=10)
path = "myqr.png"
#Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
img = ImageTk.PhotoImage(Image.open(path))
#The Label widget is a standard Tkinter widget used to display a text or image on the screen.
panel = tk.Label(thankYouPage, image = img)
panel.pack(side = "bottom", fill = "both", expand = "yes")
content=Label(thankYouPage,text="Thank you for shopping with us! \n We have mailed you the E-Bill to the entered email!").place(x=110,y=50)
content=Label(thankYouPage,text="Please scan the QR Code below if you are logging in as GUEST!").place(x=110,y=70)
button=tk.Button(thankYouPage,text='Close',fg="white",width=30,bg="black",command=thankYouPage.destroy)
button.place(x=150,y=400)

thankYouPage.mainloop()