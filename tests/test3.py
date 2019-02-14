import sqlite3

conn = sqlite3.connect('netgrok.db')
print "Opened database successfully";

conn.execute("INSERT INTO NETGROK (ID, SRC_IP, SRC_PORT, DST_IP, DST_PORT, TIME_START, TIME_END, DOWNLOAD, UPLOAD, PROTOCOL, HOST) \
      VALUES (0, '192.168.1.1', '7188', '162.221.202.8', '443', '2018-10-10 15:49:32', '2018-10-10 15:49:33', '364', '836', 'HTTPS', 'google.com')");

conn.execute("INSERT INTO NETGROK (ID, SRC_IP, SRC_PORT, DST_IP, DST_PORT, TIME_START, TIME_END, DOWNLOAD, UPLOAD, PROTOCOL, HOST) \
      VALUES (1, '192.168.1.1', '7188', '162.221.202.8', '443', '2018-10-10 15:49:34', '2018-10-10 15:49:36', '364', '836', 'HTTPS', 'amazon.com')");

conn.execute("INSERT INTO NETGROK (ID, SRC_IP, SRC_PORT, DST_IP, DST_PORT, TIME_START, TIME_END, DOWNLOAD, UPLOAD, PROTOCOL, HOST) \
      VALUES (2, '192.168.1.2', '7188', '162.221.202.8', '443', '2018-10-10 15:49:34', '2018-10-10 15:49:36', '364', '836', 'HTTPS', 'amazon.com')");

conn.execute("INSERT INTO NETGROK (ID, SRC_IP, SRC_PORT, DST_IP, DST_PORT, TIME_START, TIME_END, DOWNLOAD, UPLOAD, PROTOCOL, HOST) \
      VALUES (3, '192.168.1.2', '7188', '162.221.202.8', '443', '2018-10-10 15:49:32', '2018-10-10 15:49:33', '364', '836', 'HTTPS', 'google.com')");


conn.commit()
conn.close()
