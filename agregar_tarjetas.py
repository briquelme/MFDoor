import sqlite3
import RPi.GPIO as GPIO
import mfrc522
import signal
from operator import methodcaller

# Code used to add allowed tags to a small sqlite db.
# TODO: 
# * rewrite code for better documentation and class/package structure.
# * Test for python3 and pip packages on a rpi3 or newer


# Creating cursor to sqlite file.
# TODO: create blank file if not present. Handle with a encapsulation (read 
# purgar_base.py)
data=sqlite3.connect("usr.db")
c=data.cursor()


# Handling Ctrl+C for loop exit. Free GPIO from rpi on SIGINT
continuar_leyendo=True
def salida(signal,frame):
    global continuar_leyendo
    print ("Cerrando Programa...")
    continuar_leyendo=False
    GPIO.cleanup()
    return 0
signal.signal(signal.SIGINT, salida)

# Setting up object for tag reader
# TODO: handling errors (not connected, using different pins, etc.)
lector=mfrc522.MFRC522()

#Loop for tag registration
while continuar_leyendo:
    print ("Acerque tarjeta para agregar a db.")
    (status,Tag)=lector.MFRC522_Request(lector.PICC_REQIDL)
    #Check if tag was succesfully read
    if status==lector.MI_OK:
        print("Tarjeta detectada")
    #Fetch data from tag    
    (status,uid)=lector.MFRC522_Anticoll()
    #Remove '0x' header from uid, store as string
    if status==lector.MI_OK:
        aux=map(hex,uid[:4])
        aux=map(methodcaller("replace","0x",""),aux)
    idhex="".join(aux)#id en hex como string
    #Ask for owner name, save to db. Table 'tarjetas' has columns 'idTag' and 'nombreTag'
    nombre=str(raw_input("Ingrese nombre del propietario: "))
    linea=(idhex,nombre)
    c.execute("INSERT INTO tarjetas VALUES (?,?)",linea)
#Once loop is closed, transactions are commited and connection is closed.
data.commit()
data.close()

