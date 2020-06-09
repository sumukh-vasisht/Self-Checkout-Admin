import requests
import cv2
import numpy as np
from pyzbar import pyzbar
import argparse
import os
import re
import glob
import tkinter as tk
from tkinter import *
import smtplib
from prettytable import PrettyTable
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import csv
from PIL import ImageGrab
import time
import multiprocessing
from tabulate import tabulate
import pyrebase
import firebase_admin as firebase
from firebase_admin import firestore, storage
import json
from datetime import date
import pyqrcode 
import png 
from pyqrcode import QRCode 
from PIL import ImageTk, Image

today = date.today()
date=str(today)
print(date)

items=[]
itemScanned=[]
quantity=[]
prices=[]

fruitsAndVegetables=['Apple','Mango','Banana','Litchi','Orange','Pomogranate','Cheeku','Muskmelon'
                    ,'Watermelon','Beetroot','Beans','Carrot','Radish']
liquids=['Pepsi','Coca-Cola','Tropicana','Harpic','Maaza']

url="http://192.168.0.104:8080/shot.jpg"

def showThankYouPage():
    s = QRCodeData
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

def sendEBill():
    senderAddress = 'selfcheckoutsample@gmail.com'
    senderPassword = '@Sample123'
    server = 'smtp.gmail.com:587'
    recieverAddress = email

    with open('totalPrice.txt','r') as f:
        totalPrice=f.read()
        f.close()

    text = """
    Dear Customer,

    Thank you for shopping with us!
    Please find your E-Bill down below : 

    {table}

    Regards,
    ABC Mart
    """

    html = """
    <html>

    <head>
        <style> 
            table, th, td, tr {{ border: 1px solid red; border-collapse: collapse; }}
            th, td{{ border-left:1px solid red; border-right: 1px solid red;}}
        </style>
    </head>

    <body>
        <p>Dear Customer,</p>
        <p>Thank you for shopping with us! <br/>
        Please find your E-Bill down below : </p><br/>
        {table}
        <br/>
        <p>Total Price : Rs. %s /-</p><br/><br/>
        <p>Regards,</p><br/>
        <p>ABC Mart</p>
    </body>

    </html>
    """ %totalPrice

    data=[]

    with open('data.csv') as f:
        data=[line.split() for line in f]

    text = text.format(table=tabulate(data, headers="firstrow", tablefmt="grid"))
    html = html.format(table=tabulate(data, headers="firstrow", tablefmt="html"))

    message = MIMEMultipart("alternative", None, [MIMEText(text), MIMEText(html,'html')])

    message['Subject'] = "ABC Mart E-Bill"
    message['From'] = senderAddress
    message['To'] = recieverAddress
    server = smtplib.SMTP(server)
    server.ehlo()
    server.starttls()
    server.login(senderAddress, senderPassword)
    server.sendmail(senderAddress, recieverAddress, message.as_string())
    print('Email Sent')
    server.quit()

def navigateToPageFour():
    if emailExists:
        userDetails = db.collection('users').document(email).get().to_dict()
        currentBillNumber = userDetails['billQuantity']
        nextBillNumber = currentBillNumber + 1
        userDetails['billQuantity']=nextBillNumber
        db.collection('users').document(email).set(userDetails)

        documentID = email+str(nextBillNumber)
        print(documentID)

        totalPrice=0

        slNo=int(1)

        for i in range(len(items)):
            index1='item'+str(slNo)
            index2='quantity'+str(slNo)
            index3='price'+str(slNo)
            if i==0:
                existing={}
            else:
                existing = db.collection('bills').document(documentID).get().to_dict()
            print('**************************************************************')
            print(existing)
            existing['date']=date
            existing[index1]=itemScanned[i] 
            existing[index2]=quantity[i] 
            existing[index3]=prices[i] 
            totalPrice+=int(prices[i])
            existing['totalPrice'] = totalPrice
            db.collection(u'bills').document(documentID).set(existing)
            slNo += 1
    else:
        global QRCodeData
        userDetails = db.collection('guests').document('guestNumber').get().to_dict()
        currentBillNumber = userDetails['number']
        nextBillNumber = currentBillNumber + 1
        userDetails['number']=nextBillNumber
        db.collection('guests').document('guestNumber').set(userDetails)

        documentID = 'guest'+str(nextBillNumber)
        QRCodeData = documentID
        print("QRCODEDAT = ",QRCodeData)
        print(documentID)

        totalPrice=0

        slNo=int(1)

        for i in range(len(items)):
            index1='item'+str(slNo)
            index2='quantity'+str(slNo)
            index3='price'+str(slNo)
            if i==0:
                existing={}
            else:
                existing = db.collection('guests').document(documentID).get().to_dict()
            print('**************************************************************')
            print(existing)
            existing['date']=date
            existing[index1]=itemScanned[i] 
            existing[index2]=quantity[i] 
            existing[index3]=prices[i] 
            totalPrice+=int(prices[i])
            existing['totalPrice'] = totalPrice
            db.collection(u'guests').document(documentID).set(existing)
            slNo += 1
    sendEBill()
    billPage.destroy()
    showThankYouPage()

def writeToFile():
    pointerLocal=0
    
    with open('data.csv','w',newline='') as f:
        f.write('SlNo Item Quantity Price')
        for item in itemScanned:
            f.write('\n')
            temp=str(pointerLocal+1)+' '+itemScanned[pointerLocal]+' '+quantity[pointerLocal]+' '+prices[pointerLocal]
            f.write(temp)
            pointerLocal+=1

def showBillPage():

    writeToFile()

    global billPage
    billPage=tk.Tk()
    billPage.title("ABC Mart")
    billPage.geometry("500x500+300-100")
    title=Label(billPage,text="BILL DETAILS", font=('comicsana',18)).place(x=170,y=10)

    slNo=1
    slNox=10
    slNoy=50
    itemNamex=70
    itemNamey=50
    quantityx=250
    quantityy=50
    pricex=350
    pricey=50
    discountx=420
    discounty=50
    pointer=0
    totalPrice=0

    title=Label(billPage,text="SL NO").place(x=slNox,y=slNoy)
    title=Label(billPage,text="ITEM").place(x=itemNamex,y=itemNamey)
    title=Label(billPage,text="QUANTITY").place(x=quantityx,y=quantityy)
    title=Label(billPage,text="PRICE").place(x=pricex,y=pricey)
    title=Label(billPage,text="DISCOUNT").place(x=discountx,y=discounty)

    slNoy += 20
    itemNamey += 20
    quantityy += 20
    pricey += 20
    discounty += 20

    name=''

    for item in itemScanned:
        if item in fruitsAndVegetables:
            name='Kgs'
        elif item in liquids:
            name='Lts'
        else:
            name='Units'
        title=Label(billPage,text=slNo).place(x=slNox,y=slNoy)
        title=Label(billPage,text=item).place(x=itemNamex,y=itemNamey)
        title=Label(billPage,text=quantity[pointer]+" "+name).place(x=quantityx,y=quantityy)
        title=Label(billPage,text=prices[pointer]+'/-').place(x=pricex,y=pricey)
        title=Label(billPage,text="None").place(x=discountx,y=discounty)

        totalPrice += int(prices[pointer])

        slNo += 1
        slNoy += 20
        itemNamey += 20
        quantityy += 20
        pricey += 20
        discounty += 20
        pointer+=1

    with open('totalPrice.txt','w') as f:
        f.write(str(totalPrice))
        f.close()

    totalPriceLabel=Label(billPage,text="TOTAL PRICE : "+str(totalPrice)).place(x=itemNamex,y=discounty+20)
    button=tk.Button(billPage,text='Pay '+str(totalPrice),fg="white",width=30,bg="black",command=navigateToPageFour)
    button.place(x=130,y=200)
    billPage.mainloop()

def getBarCodes():
    while True:
        imageResponse=requests.get(url)
        imageArray=np.array(bytearray(imageResponse.content),dtype=np.uint8)
        image=cv2.imdecode(imageArray,-1)
        imS=cv2.resize(image,(900,500))
        cv2.imshow("AndroidCam",imS)
        bars=pyzbar.decode(image)
        if bars:
            for bar in bars:
                (x,y,w,h)=bar.rect
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),2)
                barcodeData=bar.data.decode("utf-8")
                barcodeType=bar.type

                text="{}({})".format(barcodeData,barcodeType)
                splStr='('
                res=text.partition(splStr)[0]
                print(res)
                if res not in items:
                    items.append(res) 
                    itemName,quant,pri,itemID=map(str,res.split())
                    itemScanned.append(itemName)
                    quantity.append(quant)
                    prices.append(pri)
            cv2.waitKey(100)
        if cv2.waitKey(1)==27:
            cv2.destroyAllWindows()
            showBillPage()
            break

def navigateToPageThree():
    statusPage.destroy()
    getBarCodes()
    return

def showStatus():
    userDetails = db.collection('users').document(email).get().to_dict()
    global statusPage
    global emailExists
    statusPage=tk.Tk()
    statusPage.title("ABC Mart")
    statusPage.geometry("500x500+300-100")
    title=Label(statusPage,text="ACCOUNT STATUS", font=('comicsana',18)).place(x=150,y=10)
    if(userDetails==None):
        title=Label(statusPage,text="Account associated with the entered Email ID NOT FOUND!").place(x=100,y=100)
        title=Label(statusPage, text="Please use GUEST LOGIN method to pay").place(x=100,y=120)
        emailExists=False
    else:
        title=Label(statusPage,text="An account associated with the entered Email ID exists!").place(x=100,y=100) 
        title=Label(statusPage, text="Please login on your mobile to pay").place(x=100,y=120)
        emailExists=True
    button = tk.Button(statusPage,text='Proceed',fg="white",width=30,bg="black",command=navigateToPageThree)
    button.place(x=140,y=200)
    statusPage.mainloop()  

def navigateToPageTwo():
    global email
    email = entry1.get()
    phoneNumber = entry2.get()
    print(email, phoneNumber)
    mainWindow.destroy()
    showStatus()

#--------------------------------FOR FIRESTORE----------------------------

cred = firebase.credentials.Certificate("firebaseKey.json")
keyFile = open('pyrebaseKey.json','r')
keyJson = keyFile.read()
key = json.loads(keyJson)

firebase.initialize_app(cred,{'storageBucket':'selfcheckout-8b125.appspot.com'})
db = firestore.client() #For database
bucket = storage.bucket()
auth = pyrebase.initialize_app(key).auth() #For authentication

#-------------------------------------FIRESTORE ENDS--------------------------

#-------------------------------------MAIN WINDOW-----------------------------

mainWindow = tk.Tk()
mainWindow.title('ABC Mart')
mainWindow.geometry("500x500+300-100")
frame = tk.Frame(mainWindow)

#----------------------------------MAIN WINDOW ENDS---------------------------

#-----------------------------------PAGE1------------------------------------------------------

title = Label(mainWindow,text="ENTER DETAILS", font=('comicsana',18)).place(x=150,y=10)
tk.Label(mainWindow, text="Email-ID", font=('comicsana',13)).place(x=90,y=100)
tk.Label(mainWindow, text="Phone Number", font=('comicsana',13)).place(x=90,y=150)
entry1 = tk.Entry(mainWindow, width=30)
entry1.place(x=240,y=100)
entry2 = tk.Entry(mainWindow, width=30)
entry2.place(x=240,y=150)
button = tk.Button(mainWindow,text='Proceed',fg="white",width=30,bg="black",command=navigateToPageTwo)
button.place(x=130,y=200)

#------------------------------------PAGE 1 ENDS------------------------------------------------

mainWindow.mainloop()
