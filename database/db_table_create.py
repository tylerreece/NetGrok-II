#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('netgrok.db')
print "Opened database successfully";

conn.execute('''CREATE TABLE NETGROK
         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
	 SRC_IP     TEXT	NOT NULL,
	 SRC_PORT   TEXT        NOT NULL,
	 DST_IP     TEXT        NOT NULL,
         DST_PORT   TEXT	NOT NULL,
         TIME_START TEXT        NOT NULL,
         TIME_END   TEXT        NOT NULL,
         DOWNLOAD   TEXT        NOT NULL,
         UPLOAD     TEXT        NOT NULL,
         PROTOCOL   TEXT        NOT NULL,
         HOST       TEXT        NOT NULL
	  );''')
print "Table created successfully";

conn.close()
