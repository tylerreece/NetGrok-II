from subprocess import call

#remove netgrok db
call(["rm", "netgrok.db"])

#call db create
call(["python", "db_create.py"])

# call db table create
call(["python", "db_table_create.py"])


