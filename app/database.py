import mysql.connector

# https://www.w3schools.com/python/python_mysql_getstarted.asp
# for how to use the database keyword in connect (**kwargs): https://www.w3schools.com/python/python_mysql_create_db.asp
# reset root password MySQL installed locally:
# https://www.a2hosting.com/kb/developer-corner/mysql/reset-mysql-root-password
# https://stackoverflow.com/questions/59941858/how-to-set-root-password-in-mariadb-10-4-on-macos#59942747
# login by: "mysql -u root -p" getting prompted for the password
mydb = mysql.connector.connect(

)

cursor = mydb.cursor()

create_first_table = "CREATE TABLE IF NOT EXISTS files " \
                     "(id INT AUTO_INCREMENT PRIMARY KEY," \
                     "path VARCHAR(255)," \
                     "creation_date DATETIME"

look_for_tables = "SHOW TABLES"

cursor.execute(look_for_tables)

for x in cursor:
    print(x)

# from pymongo import MongoClient
# # pprint library is used to make the outpu look more pretty
# from pprint import pprint
#
# # connect to MongoDB cluster
# # remember to configure IP addr access in mongoDB cloud management
# # connected through pem certificates (create new)
# client = MongoClient()
#
# class ConnectToMongoDB:
#     def __init__(self):
#         pass
#
#     def is_mongodb_installed(self):
#         # TODO check for working MongoDB installation
#         pass
#
#     def setup(self):
#         pass
