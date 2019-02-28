import sqlite3

conn = sqlite3.connect('netgrok.db')
cursor = conn.execute("SELECT * from NETGROK")
print(cursor.fetchall())
conn.close()
