import mysql.connector
from flask import jsonify



def dbTable():
    mydb = mysql.connector.connect(
    host="localhost",
    user="sagar",
    password="sagar",
    database="clouddb"
    )
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS tbl_create_user(u_id bigint Auto_Increment Primary Key,u_email varchar(45) Unique, u_password varchar(255) DEFAULT NULL,u_fname varchar(45)  DEFAULT NULL,u_lname varchar(45)  DEFAULT NULL,acc_created varchar(45)  DEFAULT NULL,acc_updated varchar(45) DEFAULT NULL) ENGINE=InnoDB AUTO_INCREMENT=1")
    mycursor.close()
   
def dbConnection():
   

    mydb = mysql.connector.connect(
    host="localhost",
    user="sagar",
    password="sagar"
    )

    mycursor = mydb.cursor()

    mycursor.execute("Create Database If NOt EXISTS clouddb")
    mycursor.close()




dbConnection()
dbTable()

SqlAlchemy = mysql.connector.connect(host="localhost",user="sagar",password="sagar",database="clouddb")
