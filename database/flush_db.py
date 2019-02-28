from subprocess import call

#remove netgrok db
call(["rm", "netgrok.db"])

#call db create
call(["python", "create.py"])

# call db table create
call(["python", "table_create.py"])


