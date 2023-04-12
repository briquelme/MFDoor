import RPi.GPIO as GPIO
import MFRC522
import time
import signal
import sqlite3
from operator import methodcaller

# Code used to operate a door with the usage of RFID tags, and using small 
# LED diodes to inform user if access was granted.
# TODO:
# * Rewrite code for better documentation and more elegant loop handling
# * Add support for door relay or similar mechanism.
# * Define wich RFID/NFC readr and tags are compatible.
# * Test for python3 and pip packages on rpi3 or newer.
# * Establish a working 'requirements.txt' file



# Cursor for SQLite file.
# TODO: handle if file missing. Encapsulate this behaviour
data=sqlite3.connect("usr.db")
c=data.cursor()

# Clear GPIO pins for LED diodes:
# * Pin 17 for 'Access Granted' (Green). Could also be used to control a door
#	relay.
# * Pin 21 for 'Access Denied' (Red)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(21,GPIO.OUT)


# Crtl+C Handling. Free GPIO from rpi on SIGINT
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
lector=MFRC522.MFRC522()

# Main loop. Waits for a tag to be read, fetchs id and checks on SQLite DB:
# * Id in table: access granted and use name for a short greeting.
# * Id not found: access denied
while continuar_leyendo:
	#Wait and get data from tag
	(status,Tag)=lector.MFRC522_Request(lector.PICC_REQIDL)
	if status==lector.MI_OK:
		print("Tarjeta detectada")
	(status,uid)=lector.MFRC522_Anticoll()
	#Get ID and remove '0x' header
	if status==lector.MI_OK:
		aux=map(hex,uid[:4])
		aux=map(methodcaller("replace","0x",""),aux)#aux es lista de la id como hex
	idhex="".join(aux)#id en hex como string
	# Search in DB.
	c.execute("SELECT * FROM tarjetas WHERE uid=?", (idhex,))
	# Fetch one row.
	# TODO: improve table design
	a=c.fetchone()
	# Row not found: access denied
	if a==None:
		print ("Acceso denegado")
		GPIO.output(21,True)
		# Timeout 2 seconds, avoid repeated reads from same tag
		time.sleep(2)
		GPIO.output(21,False)
	# At least 1 row found in db.
	else:
		#Small greeting
		print ("Bienvenido "+str(a[1]))
		GPIO.output(17,True)
		# Timeout 2 seconds, avoid repeated reads from same tag
		time.sleep(2)
		GPIO.output(17,False)
