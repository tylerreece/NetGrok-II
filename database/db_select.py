#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('netgrok.db')
print "Opened database successfully";

cursor = conn.execute("SELECT * from NETGROK")
print(cursor.fetchall())

print "Operation done successfully";
conn.close()
