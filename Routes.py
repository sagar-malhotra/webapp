from App import app
from flask import Flask as flsk
import logging
import sys
from logging import FileHandler,WARNING
from Db import SqlAlchemy as mysql
from flask import jsonify,request
from flask import abort, request
import uuid
import boto3
import base64
import email
import errno
import pymysql
import json
import statsd
import time
from dotenv import load_dotenv
from pathlib import Path
from http.client import BAD_REQUEST
import requests
from multiprocessing.connection import wait
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import bcrypt
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler = logging.FileHandler('webapplogs.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



s3=boto3.client('s3')
s =b'$2b$12$5bLd8.tAyVOYX66Y2KLNROtA86OappyUFvMtpSYsMDGnH2z1HNnUO'
c = statsd.StatsClient('localhost',8125)
dotenv_path = Path("/home/ubuntu/.env")
load_dotenv(dotenv_path=dotenv_path)
bucket_name=os.environ['S3_Name']

# bucket_name="buckettest"


@app.route('/v1/documents/<string:docId>', methods=['DELETE'])
def document_delete(docId):
    csr = None
    start=time.time()
    c.incr("Delete Document")
    try:
         auth_token=str(request.headers['Authorization'])[6:]
         check_auth=authenticate_user(auth_token)
                  
         if check_auth != False:			
            # bucket_name="testcsye"
            u_id=check_auth
            csr = mysql.cursor()
            query = "SELECT u_filename,s3_bucket_path,u_id from tbl_document_user where doc_id= %s"
            field = (docId,)
            csr.execute(query, field)
            data=csr.fetchone()
            if data is None:
                csr.close()
                result = jsonify({"Not found",404})
                result.status_code = 404			
                return result
            file_name=data[0]
            bucket_path=data[1]
            u_id_db=data[2]
            if(u_id!= u_id_db):
                csr.close()			
                result = jsonify({"User unauthorized":'401'})
                result.status_code = 401
                return result
           
            response=s3.delete_object(Bucket=bucket_name, Key=docId)

            csr.close()   
            csr=mysql.cursor()            
            query="Delete from tbl_document_user where doc_id=%s"
            field=(docId,)    
            csr.execute(query,field)   
            mysql.commit() 
            result=jsonify({"No Content":"204"})
            result.status_code=204
            csr.close()
            app.logger.info("User deleted successfully")
            duration = (time.time() - start) *1000
            c.timing("deleteapi time",duration)
            return result
         else:
            resp=jsonify({'Unauthorized User':'401'})
            resp.status_code=401
            
            app.logger.error("User not deleted")
            return resp					
 
    except Exception as e:
        success=True
        app.logger.error("User not deleted bad request")

    if success:
        resp=jsonify({"Bad Request":"400"})
        resp.status_code=400
        return resp
 

@app.route("/healthz")
def healthy_app():
    start=time.time()
    c.incr("healthz")
    app.logger.info("Healthy Application")
    duration = (time.time() - start) *1000
    c.timing("healthzapi time",duration)
    return jsonify({"Application is healthy": "200"})

@app.route("/app")
def health_app():
    start=time.time()
    c.incr("app")
    app.logger.info("Health Application")
    duration = (time.time() - start) *1000
    c.timing("App time",duration)
    return jsonify({"Application is healthy": "200"})

@app.route('/v1/documents', methods=['POST'])
def upload_document():
    start=time.time()
    c.incr("Document Upload")
    if 'files[]' not in request.files:
     
       resp=jsonify({'message': 'Please provide the validate key'})
       resp.status_code=400
       return resp
    files=request.files.getlist('files[]')
    
    csr = None
    db_error=False

    auth_token=str(request.headers['Authorization'])[6:]
    #Basic Auth
    check_auth=authenticate_user(auth_token)
    
    file_count=len(files)
    try:
        if check_auth != False:
            u_id=check_auth
            for file in files:
                if file and file_count==1:
				
                    filename=secure_filename(file.filename)
                    pathname=os.path.join("/home/ubuntu/",filename)
                    file.save(os.path.join("",filename))
                    # bucket_name will be passed by environment variables
                    object_name=str(uuid.uuid4())
                    s3.upload_file(pathname,bucket_name,object_name)
                    s3_bucket_path="/"+bucket_name+"/"+object_name
                    head_object=s3.head_object(Bucket=bucket_name,Key=object_name)
                    created_date_s3=head_object.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('date')
                    
                    # insert data into db
                    query = "INSERT INTO tbl_document_user(doc_id, u_id, u_filename,Date_created,s3_bucket_path) VALUES(%s,%s,%s,%s,%s)"
                    field = (object_name,u_id,filename,created_date_s3,s3_bucket_path)
                    csr = mysql.cursor()
                    csr.execute(query, field)       
                    mysql.commit()
                    csr.close()		
                    csr = mysql.cursor(dictionary=True)        
                    query = "SELECT doc_id, u_id, u_filename,Date_created, s3_bucket_path from tbl_document_user where doc_id= %s"
                    field = (object_name,)
                    csr.execute(query, field)
                            
                    data=csr.fetchone()
                        
                    resp = jsonify(data)
                    resp.status_code = 201
                    csr.close()
                    app.logger.info("Document updated")
                    duration = (time.time() - start) *1000
                    c.timing("uploaddocumentapi time",duration)     
                    return resp
                else:
                    csr=mysql.cursor()
                    resp=jsonify({'message':'More than 1 file can not be uploaded'})
                    resp.status_code=400
                    csr.close()
                    app.logger.error("More than 1 file can not be uploaded")
                    return resp


        else:
            app.logger.error("Authorization error") 
            resp=jsonify({'message':'Authorization Error'})
            resp.status_code=400
            return resp

    except Exception as e:
	# print(e)
        db_error=True
        app.logger.error("file upload bad request") 

    if db_error:
        resp=jsonify({"Bad Request":"400"})
        resp.status_code=400
        return resp



@app.route('/v1/documents/<string:DocId>',methods=['GET'])
def get_document(DocId):
    start=time.time()
    c.incr("Delete Document")
    csr = None
    auth_token=str(request.headers['Authorization'])[6:]
    check_auth=authenticate_user(auth_token)
    db_error=False
    try:
        if check_auth != False:
            u_id=check_auth
            csr = mysql.cursor(dictionary=True)
            query = "SELECT doc_id, u_id, u_filename, Date_created, s3_bucket_path from tbl_document_user where doc_id= %s"  
            field = (DocId,)
            csr.execute(query, field)
            data=csr.fetchone()
            Db_id=data["u_id"]
            if(u_id!= Db_id):
                csr.close()			
                resp = jsonify({"User unauthorized":'401'})
                resp.status_code = 401
                return resp

            if(data is None):
				
                csr.close()
                resp=jsonify("Bad Request",400)
                resp.status_code=400

                return resp

            csr.close()			
            resp = jsonify(data)
            resp.status_code = 201
            app.logger.info("Document fetched successfully") 
            duration = (time.time() - start) *1000
            c.timing("getdocumentapi time",duration)				
            return resp
        else:
           
            resp=jsonify({'Unauthorized User':'401'})
            resp.status_code=401
            app.logger.error("Document not fetched") 
            return resp  

    except Exception as e:
        db_error=True
        app.logger.error("Document not fetched bad request") 
        # print(e)

    if db_error:
        resp=jsonify({"Bad Request":"400"})
        resp.status_code=400
        return resp
  

@app.route('/v1/documents', methods=['GET'])
def get_documents():
    start=time.time()
    c.incr("Get all documents")
    csr = None
    db_error=False
    auth_token=str(request.headers['Authorization'])[6:]
    check_auth=authenticate_user(auth_token)
    try:
        if check_auth != False:
            u_id=check_auth
            csr = mysql.cursor()
            query = "SELECT doc_id, u_id, u_filename, Date_created, s3_bucket_path from tbl_document_user where u_id= %s"
            field = (u_id,)
            csr.execute(query, field)
            data=csr.fetchall()
            csr.close()
            doc_list=[]
            for rows in data:
                
                doc_list.append(rows)
            result = jsonify(doc_list)
            result.status_code = 201
            app.logger.info("Documents fetched successfully") 	
            duration = (time.time() - start) *1000
            c.timing("getalldocumentsapi time",duration)			
            return result
        else:
            resp=jsonify({'Unauthorized User':'401'})
            resp.status_code=401
            app.logger.error("Documents not fetched") 
            return resp

    except Exception as e:
        db_error=True
        app.logger.error("Documents not fetched bad request") 
        # print(e)

    if db_error:
        resp=jsonify({"Bad Request":"400"})
        resp.status_code=400
        return resp

@app.route('/v1/verifyUserEmail/<string:EmailId1>',methods=['GET'])
def insertvalueindynamodb(EmailId1):
    EmailId=EmailId1+"'"
    csr =None
    db_error=False
    app.logger.info("Test")
    try:
        app.logger.info(EmailId)
        x = EmailId.split("=")
        app.logger.info(x)
        token=x[2]
        app.logger.info(token)
        y=x[1].split("&")
        emailid=y[0]
        app.logger.info(emailid)
        app.logger.info("test10")
        dynamodb=boto3.resource('dynamodb',region_name='us-east-1')
        app.logger.info("test11")
        table=dynamodb.Table('UserDetails')
        app.logger.info("test12")
        response=table.get_item(
                Key={
                   "Email":emailid,
                   "Token":token
                }
        )
        app.logger.info(response)
        if response['Item']:
            app.logger.info("test14")
            query = "update tbl_create_user set verified_user =%s where u_email=%s"
            field = ("YES",emailid)
            csr = mysql.cursor()

            csr.execute(query, field)
            app.logger.info("test15")
            mysql.commit()
            csr.close()	
            result=jsonify(Message="User Verified", Code = 200  )
            result.status=200
            return result
            
    except Exception as e:
        db_error=True
        app.logger.error("User details not verified") 	
        app.logger.error(e.__traceback__.tb_lineno) 
        app.logger.error(e)		
			
		
    if db_error:
		
        result=jsonify(Error="User Not Verfied", Code = 400  )	
        result.status=400
        return result




@app.route('/v1/account', methods=['POST'])
def userDetails():
	start=time.time()
    
	c.incr("post user details")
	csr =None
	db_error=False
	try:
	
		js = request.json
		email =js['email']
		password =js['password']
		fname =js['fname']
		lname=js['lname']
		
		
		now = datetime.now()
		
		u_crdate = now.strftime("%d/%m/%Y %H:%M:%S")
		
		if fname and lname and email and password and request.method == 'POST':
			# bcrypt password
			bytes = password.encode('utf-8')
			app.logger.info(password)	
			app.logger.info("test1")
			Get_Token=tokenauthenticate(email,password)
			app.logger.info("test8")
			hash_pwd = bcrypt.hashpw(bytes, s)
			app.logger.info("test9")
			u_verified="NO"
			query = "INSERT INTO tbl_create_user(u_email, u_password, u_fname, u_lname,acc_created,verified_user) VALUES(%s,%s,%s,%s,%s,%s)"
			field = (email,hash_pwd,fname,lname,u_crdate,u_verified)
			csr = mysql.cursor()
			app.logger.info("test8")
			csr.execute(query, field)
			
			mysql.commit()
			
			# rows = csr.fetchone()
			csr.close()	
			
			csr = mysql.cursor(dictionary=True)
			
			client = boto3.client('sns',region_name='us-east-1')
			response = client.publish (
            TargetArn = "arn:aws:sns:us-east-1:868454036435:CSYETopic_assignment8",
            Message = json.dumps(
                {'email':email,
                 'token':Get_Token,
                 'Message_Type':"user verification"
                })
                 )

			query = "SELECT u_id,u_email,u_fname,u_lname,verified_user from tbl_create_user where u_email= %s"
			field = (email,)
			csr.execute(query, field)
			
			data=csr.fetchone()
		
			result = jsonify(data)
			
			app.logger.info("User details added successfully") 
			result.status_code = 201
			duration = (time.time() - start) *1000
			c.timing("postuserdetailsapi time",duration)           
			csr.close()
			return result
		else:
			db_error=True
			app.logger.error("User details not added")          
            
	
	except Exception as e:
		# print(e) 
		db_error=True
		app.logger.error(e.__traceback__.tb_lineno) 
		app.logger.error(e)		
		
	if db_error:
		
		result=jsonify(Error="BAD_REQUEST", Code = 400  )	
		result.status=400
		return result
		

def authenticate_user(auth_token):
    csr = None
    db_error=False

    try:
        csr = mysql.cursor()
       	
        auth_token1=base64.b64decode(auth_token)
				
        auth_split=str(auth_token1).split(':')
        auth_uname=str(auth_split[0])[2:]
        
        auth_pwd=str(auth_split[1])
				
        hash_pwd=pwd(auth_pwd[:-1])
        query="Select u_password pwd,u_id, verified_user from tbl_create_user where u_email=%s"
        field=(auth_uname,)
        csr.execute(query,field)
        rec=csr.fetchone()
        db_pwd=rec[0]
        db_uid=rec[1]
        db_verified=rec[2]
        if(rec is None):				
            csr.close()
            return False
        else:
            csr.close()
				
            if((str(hash_pwd)[2:].replace('\'','')==db_pwd) and db_verified=="YES"):
                return db_uid
            else:

                return False
					
    except Exception as e :
        db_error=True

    if db_error:
        return False


def tokenauthenticate(email,password):

       
    combination=email+":"+password
    app.logger.info(combination)	
    app.logger.info("test2")
    token= str(combination.encode('utf-8'))
    app.logger.info("test3")
    expiryTimestamp = int(time.time() + 2*60)	
    app.logger.info("test4")		
    
    dynamodb=boto3.resource('dynamodb',region_name='us-east-1')
    app.logger.info("test5")
    table = dynamodb.Table('UserDetails')
    table.put_item(
    Item={
        'Email': email,
        'Token': token,
        'TTL':expiryTimestamp,
    }
)   
    app.logger.info("test6")
    return token

@app.route('/v1/account/<int:Id>',methods=['GET'])
def user(Id):	
	start=time.time()
	c.incr("Get user details")
	db_error = False
	csr = None
	try:
		
		if Id:
			
			#dbcon = mysql.connect()
			
			csr = mysql.cursor()
			query="Select u_email, u_password,verified_user from tbl_create_user where u_id=%s"
			field=(Id,)
			csr.execute(query,field)
			
			rec=csr.fetchone()
			
			if(rec is None):
				
				csr.close()
				result=jsonify("Bad Request",400)
				result.status_code=400
				app.logger.error("User details does not exist")               
                
				return result
			else:
				csr.close()
				
				# skipping first 6 digits
				auth_token=str(request.headers['Authorization'])[6:]
				
				auth_token1=base64.b64decode(auth_token)
				
				auth_split=str(auth_token1).split(':')
				auth_uname=str(auth_split[0])[2:]
				# print(auth_uname)


				auth_pwd=str(auth_split[1])
				
				hash_pwd=pwd(auth_pwd[:-1])

				db_pwd=rec[1]
				db_uname=rec[0]
				db_verified=rec[2]
				
				if((str(hash_pwd)[2:].replace('\'','')==db_pwd) and ((auth_uname==db_uname)and db_verified=="YES") ):
					
					csr = mysql.cursor(dictionary=True)
					query="SELECT u_id,u_email,u_fname,u_lname,acc_created,acc_updated from tbl_create_user where u_id=%s"
					field=(Id,)
					csr.execute(query,field)
					exist = csr.fetchone()
					if exist is None:
						csr.close()
						raise logging.exception
					result = jsonify(exist)
					result.status_code = 200
					csr.close()
					app.logger.info("User details fetched successfully")
					duration = (time.time() - start) *1000
					c.timing("getuserdetailsapi time",duration)
					return result

				else:
					result=jsonify("Unauthorized user",401)
					result.status_code=401
					app.logger.error("User details not fetched unauthorized user")
					return result
	except Exception as e:
		db_error=True
		
		app.logger.error("User unauthorized")

	if db_error:
		# print("duplicate error")
		result=jsonify(Error="Forbidden", Code = 403 )	
		result.status_code=403
		
		return result



@app.route('/v1/account/<int:AccId>', methods=['PUT'])
def update_userDetails(AccId):
	
	start=time.time()
	c.incr("update user details")
	csr = None
	
	try:
		
		js = request.json
		email =js['email']
		password =js['password']
		fname =js['fname']
		lname=js['lname']


		now = datetime.now()

		# dd/mm/YY H:M:S
		u_update = now.strftime("%d/%m/%Y %H:%M:%S")	
		
		# validate the received values
		if email and request.method == 'PUT':
			
			#dbcon=mysql.connect()
			csr=mysql.cursor()
			query="Select u_email em, u_password pd, verified_user from tbl_create_user where u_id=%s"
			field=(AccId,)
			csr.execute(query,field)

			rec=csr.fetchone()

			if(rec is None):
				
				csr.close()
				result=jsonify("Unauthorized User",401)
				result.status_code=401

				return result
			else:
				
				csr.close()
				
				# skipping first 6 digits
				auth_token=str(request.headers['Authorization'])[6:]
				
				auth_token1=base64.b64decode(auth_token)
				auth_split=str(auth_token1).split(':')
				auth_uname=str(auth_split[0])[2:]
				# print(auth_uname)
				auth_pwd=str(auth_split[1])
				
				hash_pwd=pwd(auth_pwd[:-1])

				db_pwd=rec[1]
				db_uname=rec[0]
				db_verified=rec[2]
				
				if((str(hash_pwd)[2:].replace('\'','')==db_pwd) and ((auth_uname==db_uname) and db_verified=="YES")):
					# print("matched")
					csr = mysql.cursor()
					# bcrypt password
					bytes = password.encode('utf-8')
					hashed_pwd = bcrypt.hashpw(bytes, s)

						# save edits
					sql = "UPDATE tbl_create_user SET u_fname=%s, u_lname=%s, u_password=%s, acc_updated=%s WHERE u_email=%s"
					data = (fname, lname, hashed_pwd,u_update,email)
					#dbcon = mysql.connect()
					csr = mysql.cursor()
					csr.execute(sql, data)
					mysql.commit()
					# print(csr.rowcount)
					if csr.rowcount==0:
						result=jsonify("Forbidden email can't be changed",403)
						result.status_code=403
						csr.close()
						app.logger.error("User email can't be changed")
						return result
						# raise logging.exception

					csr.close()					
					result = jsonify('No Content!',204)
					result.status_code = 204 
					app.logger.info("User details updated successfully")
					duration = (time.time() - start) *1000
					c.timing("updateuserdetailsapi time",duration)                    
					return result

				else:
					#dbcon = mysql.connect()
					csr = mysql.cursor()
					csr.close()
					result=jsonify("Unauthorized User",401)
					result.status_code = 401
					app.logger.info("User details can't update unauthorized user")
					return result
			
	except Exception as e:
		# print(e)
		app.logger.info("User update bad request")
		csr = mysql.cursor()
		csr.close()
		result=jsonify(Error="Bad_Request", Code = 400  )	
		
		result.status_code=400
		return result

def pwd(password):
	pd=password.encode('utf-8')
	return bcrypt.hashpw(pd,s)



@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ',
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == "__main__":
	
    app.run(host='0.0.0.0',port=5000)

