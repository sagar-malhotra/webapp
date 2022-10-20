# from Assignment_2 import app as application
import mysql.connector
from flask import jsonify
# from flaskext.mysql import MySQL


def getDbConnection():
   

    mydb = mysql.connector.connect(
    host="localhost",
    user="user",
    password="password"
    )

    mycursor = mydb.cursor()

    mycursor.execute("Create Database If NOt EXISTS clouddb")
    mycursor.close()

def createTable():
    mydb = mysql.connector.connect(
    host="localhost",
    user="user",
    password="password",
    database="clouddb"
    )
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS tbl_Create_User(u_id bigint Auto_Increment Primary Key,u_email varchar(45) Unique, u_password varchar(255) DEFAULT NULL,u_fname varchar(45)  DEFAULT NULL,u_lname varchar(45)  DEFAULT NULL,acc_created varchar(45)  DEFAULT NULL,acc_updated varchar(45) DEFAULT NULL) ENGINE=InnoDB AUTO_INCREMENT=1")
    mycursor.close()
   


getDbConnection()
createTable()
SqlAlchemy = mysql.connector.connect(host="localhost",user="user",password="password",database="clouddb")




# SqlAlchemy.init_app(application)