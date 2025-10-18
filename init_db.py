import sqlite3
conn = sqlite3.connect("database.sqlite")
cursor = conn.cursor()
f=open("schema.sql", "r")
cursor.executescript(f.read())
conn.commit()
conn.close()
