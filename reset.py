import os
import sqlite3
from sqlite3 import Error

with open('log.txt', 'w') as lg:
	lg.write('')

files = os.listdir('Results')
for file in files:
	if file=='nomedia':
		continue
	os.remove('Results/'+file)


try:
	os.remove('studentdata.db')
except Exception as e:
	pass

dbconnection=sqlite3.connect('studentdata.db')
cursorobj=dbconnection.cursor()
cursorobj.execute('''CREATE TABLE student (
 	id INTEGER PRIMARY KEY AUTOINCREMENT,
    rollno TEXT (10) NOT NULL,
    examid TEXT (3) NOT NULL,
    res DECIMAL);''')
cursorobj.execute('''CREATE TABLE blacklist (
 	id INTEGER PRIMARY KEY AUTOINCREMENT,
    rollno TEXT (10) NOT NULL,
    examid TEXT (3) NOT NULL);''')