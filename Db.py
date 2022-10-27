import mysql.connector
from flask import jsonify
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path("/home/ubuntu/.env")
load_dotenv(dotenv_path=dotenv_path)

DB_name=os.environ['DB_Name']
DB_host=os.environ['DB_host']
DB_user = os.environ['DB_User']
DB_pass = os.environ['DB_Pass']
# from flaskext.mysql import MySQL


# def getDbConnection():
   

#     mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password=""
#     )

#     mycursor = mydb.cursor()

#     mycursor.execute("Create Database If NOt EXISTS clouddb")
#     mycursor.close()

def createTable():
    mydb = mysql.connector.connect(
    host=DB_host,
    user=DB_user,
    password=DB_pass,
    database=DB_name
    )
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS tbl_create_user(u_id bigint Auto_Increment Primary Key,u_email varchar(45) Unique, u_password varchar(255) DEFAULT NULL,u_fname varchar(45)  DEFAULT NULL,u_lname varchar(45)  DEFAULT NULL,acc_created varchar(45)  DEFAULT NULL,acc_updated varchar(45) DEFAULT NULL) ENGINE=InnoDB AUTO_INCREMENT=1")
    mycursor.close()
   
def createTabledocument():
    mydb = mysql.connector.connect(
    host=DB_host,
    user=DB_user,
    password=DB_pass,
    database=DB_name
    )
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE if not exists tbl_document_user (doc_id varchar(100),u_id bigint,u_filename varchar(255) DEFAULT NULL,Date_created varchar(50) Default Null,s3_bucket_path varchar(500) Default Null)")
    mycursor.close()

# getDbConnection()
createTable()
createTabledocument()
SqlAlchemy = mysql.connector.connect(host=DB_host,user=DB_user,password=DB_pass,database=DB_name)




# SqlAlchemy.init_app(application)
