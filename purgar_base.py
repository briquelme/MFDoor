import sqlite3
#Script used to setup a blank sqlite3 db for project usage.
#TODO: tidy up code, encapsulate in a class with easy to 
#understand methods
data=sqlite3.connect("usr.db")
c=data.cursor()
c.execute("DROP TABLE IF EXISTS tarjetas")
c.execute('''CREATE TABLE tarjetas
			(uid text, nombre text)''')
data.commit()
data.close()
