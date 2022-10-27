import requests
from App import app
import base64
import email
import errno
from http.client import BAD_REQUEST
from multiprocessing.connection import wait
from flask import abort, request
import requests
from Db import SqlAlchemy as mysql
from flask import jsonify,request
import pymysql
import uuid
import boto3
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
from datetime import datetime
import bcrypt
import logging
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path("/home/ubuntu/.env")
load_dotenv(dotenv_path=dotenv_path)

bucket_name=os.environ['S3_Name']
s =b'$2b$12$5bLd8.tAyVOYX66Y2KLNROtA86OappyUFvMtpSYsMDGnH2z1HNnUO'


s3=boto3.client('s3')

@app.route("/healthz")
def myname():
    return jsonify({"Application Is Healthy": "200"})


@app.route('/v1/documents/<string:docId>', methods=['DELETE'])
def delete_doc(docId):
    csr = None

    try:
         auth_token=str(request.headers['Authorization'])[6:]
         check_auth=authenticate_user(auth_token)

    
         if check_auth != False:
			
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


            return result
         else:
            resp=jsonify({'Unauthorized User':'401'})
            resp.status_code=401
            return resp


    
    except Exception as e:
        success=True
        # print(e)

    if success:
        resp=jsonify({"Bad Request":"400"})
        resp.status_code=400
        return resp

		
	


@app.route('/v1/documents', methods=['POST'])
def upload_doc():
    if 'files[]' not in request.files:
        result=jsonify({"Enter Proper Key":"files[]"})
        result.status_code=400
        return result
    files=request.files.getlist('files[]')
    file_count=len(files)
    csr = None
    # errors={}
    success=False
    auth_token=str(request.headers['Authorization'])[6:]
    check_auth=authenticate_user(auth_token)

    try:
        if check_auth != False:
			

            u_id=check_auth
			
            for file in files:
				
			
                if file and file_count==1:
				
                    filename=secure_filename(file.filename)
                    path_name=os.path.join("/home/ubuntu/",filename)
                    file.save(os.path.join("",filename))
                    object_name=str(uuid.uuid4())
                    s3.upload_file(path_name,bucket_name,object_name)
                    head_object=s3.head_object(Bucket=bucket_name,Key=object_name)

                    created_date_s3=head_object.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('date')
                    s3_bucket_path="/"+bucket_name+"/"+object_name
      
                    query = "INSERT INTO tbl_document_user(doc_id, u_id, u_filename,Date_created,s3_bucket_path) VALUES(%s,%s,%s,%s,%s)"
                    field = (object_name,u_id,filename,created_date_s3,s3_bucket_path)
    
                    csr = mysql.cursor()

                    csr.execute(query, field)
                            
                    mysql.commit()
                            
                        # rows = csr.fetchone()
                    csr.close()	
						
                    csr = mysql.cursor()
                            
                    query = "SELECT doc_id, u_id, u_filename, Date_created, s3_bucket_path from tbl_document_user where doc_id= %s"
                    field = (object_name,)
                    csr.execute(query, field)
                            
                    data=csr.fetchone()
                        
                    result = jsonify(data)
                            
                            # result = jsonify('User added successfully!',201)
                    result.status_code = 201
                    csr.close()
                            
                    return result
                else:
                    
                    resp=jsonify({'message':'Please select one file only'})
                    resp.status_code=400
                    csr= mysql.cursor()
                    csr.close()
                    return resp


        else:
            # csr.close()
            resp=jsonify({'message':'Authorization Error'})
            resp.status_code=400
            return resp

    except Exception as e:
        success=True

    if success:
        resp=jsonify({"Bad Request":"400"})
        resp.status_code=400
        return resp



@app.route('/v1/documents/<string:DocId>',methods=['GET'])
def get_doc(DocId):
    # print(DocId)
	# if 'files[]' not in request.files:
	# 	resp=jsonify({'message': 'No file is found'})
	# 	resp.status_code=400
	# 	return resp
    
    # files=request.files.getlist('files[]')
    # file_count=len(files)
    csr = None
    # errors={}
    success=False
    auth_token=str(request.headers['Authorization'])[6:]
    check_auth=authenticate_user(auth_token)
    # print(check_auth)
    try:
        if check_auth != False:
			

            u_id=check_auth
            csr = mysql.cursor()
            #query = "SELECT doc_id, u_id, u_filename, Date_created, s3_bucket_path from tbl_document_user where doc_id= %s"
            query = "SELECT doc_id, u_id, u_filename, Date_created, s3_bucket_path from tbl_document_user where doc_id= %s"
            field = (DocId,)
            csr.execute(query, field)
            data=csr.fetchone()
            if(data is None):
				
                csr.close()
                result=jsonify("Bad Request",400)
                result.status_code=400

                return result
            u_id_db=data[1]
            if(u_id!= u_id_db):
                csr.close()			
                result = jsonify({"User unauthorized":'401'})
                result.status_code = 401
                return result
            csr.close()	

            result = jsonify(data)
            result.status_code = 201
							
            return result
        else:
            # csr.close()
            resp=jsonify({'Unauthorized User':'401'})
            resp.status_code=401
            return resp
					# #dbcon = mysql.connect()
					# csr = mysql.cursor()
					# return not_found()
						


						
					# success=True

     

    except Exception as e:
        success=True
        # print(e)

    if success:
        resp=jsonify({"Bad Request":"400"})
        resp.status_code=400
        return resp
    # else:
    #     resp=jsonify({'message':'File type is exceeding the size or multiple files are not allowed'})
    #     resp.status_code=400
    #     return resp


@app.route('/v1/documents', methods=['GET'])
def getall_doc():
	# if 'files[]' not in request.files:
	# 	resp=jsonify({'message': 'No file is found'})
	# 	resp.status_code=400
	# 	return resp
    
    # files=request.files.getlist('files[]')
    # file_count=len(files)
    csr = None
    # errors={}
    success=False
    auth_token=str(request.headers['Authorization'])[6:]
    check_auth=authenticate_user(auth_token)
    # print(check_auth)
    try:
        if check_auth != False:
			

            u_id=check_auth
            csr = mysql.cursor()
            query = "SELECT doc_id, u_id, u_filename , Date_created, s3_bucket_path from tbl_document_user where u_id= %s"
            #query = "SELECT doc_id, u_id, u_filename, Date_created, s3_bucket_path from tbl_document_user where u_id= %s"
            field = (u_id,)
            csr.execute(query, field)
            data=csr.fetchall()
            csr.close()
            list_doc=[]
            for rows in data:
                # print(rows[0])
                list_doc.append(rows)
            # print(list_doc)
            # return jsonify({list_doc:'201'})
            # return json.dumps({ [dict(ix) for ix in data]},code=201 )




            result = jsonify(list_doc)
            result.status_code = 201
            # csr.close()				
            return result
        else:
            resp=jsonify({'Unauthorized User':'401'})
            resp.status_code=401
            return resp
					# #dbcon = mysql.connect()
					# csr = mysql.cursor()
					# return not_found()
						


						
					# success=True

     

    except Exception as e:
        success=True
        # print(e)

    if success:
        resp=jsonify({"Bad Request":"400"})
        resp.status_code=400
        return resp
    # else:
    #     resp=jsonify({'message':'File type is exceeding the size or multiple files are not allowed'})
    #     resp.status_code=400
    #     return resp





@app.route('/v1/account', methods=['POST'])
def create_user():
	
	# dbcon =None
	csr =None
	success= False
	try:
		
		js = request.json
		email =js['email']
		password =js['password']
		fname =js['fname']
		lname=js['lname']
		
		# datetime object containing current date and time
		now = datetime.now()

		# dd/mm/YY H:M:S
		u_crdate = now.strftime("%d/%m/%Y %H:%M:%S")
		
		
		# validate the received values
		if fname and lname and email and password and request.method == 'POST':
			# bcrypt password
			bytes = password.encode('utf-8')
			# salt = bcrypt.gensalt()
			hash_pwd = bcrypt.hashpw(bytes, s)
			
			# insert data into db
			query = "INSERT INTO tbl_create_user(u_email, u_password, u_fname, u_lname,acc_created) VALUES(%s,%s,%s,%s,%s)"
			field = (email,hash_pwd,fname,lname,u_crdate)
			
			# # connect with mysql
			# dbcon = mysql.connect()
			csr = mysql.cursor()
			
			# # execute the query
			csr.execute(query, field)
			
			mysql.commit()
			
			# rows = csr.fetchone()
			csr.close()	
			
			csr = mysql.cursor()
			
			query = "SELECT u_id ,u_email ,u_fname ,u_lname from tbl_create_user where u_email= %s"
			field = (email,)
			csr.execute(query, field)
			
			data=csr.fetchone()
		
			result = jsonify(data)
			
			# result = jsonify('User added successfully!',201)
			result.status_code = 201
			csr.close()
			return result
		else:
			# # dbcon = mysql.connect()
			# csr = mysql.cursor()
			# return not_found()
			success=True
	# except mysql.connector.Error:
	# 	print("error duplicacy")
	except Exception as e:
		# print(e)
		success=True		
		# dbcon = mysql.connect()
		# csr = dbcon.cursor()

	# finally:
	# 	# dbcon = mysql.connect()
	# 	csr = mysql.cursor()
	# 	csr.close() 
	# 	# dbcon.close()

	if success:
		# print("duplicate error")
		result=jsonify(Error="BAD_REQUEST", Code = 400  )	
		result.status=400
		
		# return jsonify((400, 'Record Not Found')) 
		# result.status_code="400 BAD_REQUEST"
		return result
		
# @app.route('/userdetails',methods=['GET'])
# def users():
def authenticate_user(auth_token):
    csr = None
    success=False
    # print("entered auth method")
    # print(auth_token)
    try:
        csr = mysql.cursor()
        # auth_token=str(request.headers['Authorization'])[6:]
        # print("1")		
        auth_token1=base64.b64decode(auth_token)
				
        auth_split=str(auth_token1).split(':')
        auth_uname=str(auth_split[0])[2:]
        # print(auth_uname)
        auth_pwd=str(auth_split[1])
				
        hash_pwd=pwd(auth_pwd[:-1])
        # print(hash_pwd)	
       
  
        query="Select u_password pwd,u_id from tbl_create_user where u_email=%s"
        field=(auth_uname,)
        csr.execute(query,field)
        rec=csr.fetchone()
		
        
        db_pwd=rec[0]
        db_uid=rec[1]
        # print(db_pwd)
        # print(db_uid)
        # except Exception:
        #     result=jsonify("Unauthorized user", Code = 401  )	
        #     result.status_code=401
        #     return False

        if(rec is None):
				
            csr.close()
            # result=jsonify("Unauthorized user",401)
            # result.status_code=401
            return False
        else:
            csr.close()
				
            if((str(hash_pwd)[2:].replace('\'','')==db_pwd) ):
                return db_uid
            else:
                # csr.close()
                # result=jsonify("Unauthorized user",401)
                # result.status_code=401
                return False
					
    except Exception as e :
        success=True
        # print(e)
    # finally:
		
    #     csr.close() 
	# 	#dbcon.close()
    if success:
        # result=jsonify("Unauthorized user", 401)	
        # result.status_code=401
        return False


@app.route('/v1/account/<int:Id>',methods=['GET'])
def user(Id):	
	success=False
    
	csr= None
    
	try:
		# js = request.json
		# Id =js['id']
		
		if Id:
			
			#dbcon = mysql.connect()
			
			csr = mysql.cursor()
			query="Select u_email email, u_password pd from tbl_create_user where u_id=%s"
			field=(Id,)
			csr.execute(query,field)
			
			rec=csr.fetchone()
			
			if(rec is None):
				
				csr.close()
				result=jsonify("Bad Request",400)
				result.status_code=400

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
				
				if((str(hash_pwd)[2:].replace('\'','')==db_pwd) and (auth_uname==db_uname) ):
					
					csr = mysql.cursor()
					query="SELECT u_id, u_email, u_fname, u_lname, acc_created, acc_updated from tbl_create_user where u_id=%s"
					field=(Id,)
					csr.execute(query,field)
					# field = (email)
					exist = csr.fetchone()
					if exist is None:
						csr.close()
						raise logging.exception
					# rows = csr.fetchone()
					# for x in rows:
					# 	jsonify("id= ",x[0])
					# 	jsonify("Email= ",x[1])
					# 	jsonify("First Name= ",x[2])
					# 	jsonify("Last Name= ",x[3])
					# 	jsonify("Acc Created= ",x[4])
					# 	jsonify("Acc Updated= ",x[5],"\n")
						

					result = jsonify(exist)
					result.status_code = 200
					csr.close()
					return result

				else:
					result=jsonify("Unauthorized user",401)
					result.status_code=401
					return result
	except Exception as e:
		success=True
		# result=jsonify(Error="Bad_Request-No details found", Code = 400  )	
		# result.status=400
		# result.status_code=400
		# print(e)
	# finally:
		
	# 	csr.close() 
	# 	#dbcon.close()
	if success:
		# print("duplicate error")
		result=jsonify(Error="Forbidden", Code = 403 )	
		result.status_code=403
		
		# return jsonify((400, 'Record Not Found')) 
		# result.status_code="400 BAD_REQUEST"
		return result






@app.route('/v1/account/<int:AccId>', methods=['PUT'])
def update_user(AccId):
	
	#dbcon = None
	csr = None
	
	try:
		
		js = request.json
		email =js['email']
		password =js['password']
		fname =js['fname']
		lname=js['lname']

		# if(email==" " or password==" " or fname==" " or lname==" "):
			
		# 	result=jsonify("No Content",204)
		# 	result.status_code=401
		# 	return result
		
		# datetime object containing current date and time
		now = datetime.now()

		# dd/mm/YY H:M:S
		u_update = now.strftime("%d/%m/%Y %H:%M:%S")	
		
		# validate the received values
		if email and request.method == 'PUT':
			
			#dbcon=mysql.connect()
			csr=mysql.cursor()
			query="Select u_email em, u_password pd from tbl_create_user where u_id=%s"
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
				# print(rec)
				# print(type(rec))
				db_pwd=rec[1]
				db_uname=rec[0]
				
				if((str(hash_pwd)[2:].replace('\'','')==db_pwd) and (auth_uname==db_uname) ):
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
						return result
						# raise logging.exception
					# 	print("csr is none")
					# exist = csr.fetchone()
					# if exist is not None:
					csr.close()					
					result = jsonify('No Content!',204)
					result.status_code = 204
					return result

				else:
					#dbcon = mysql.connect()
					csr = mysql.cursor()
					csr.close()
					result=jsonify("Unauthorized User",401)
					result.status_code = 401
					return result
			
	except Exception as e:
		# print(e)
		#dbcon = mysql.connect()
		csr = mysql.cursor()
		csr.close()
		result=jsonify(Error="Bad_Request", Code = 400  )	
		
		result.status_code=400
		return result
		# # resp = jsonify("User can't be updated!")
		# # resp.status_code = 404
		# # return result
		# # print(e)
	# finally:
	# 	csr.close() 
	# 	#dbcon.close()
		

		

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ',
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

def pwd(password):
	pd=password.encode('utf-8')
	return bcrypt.hashpw(pd,s)


if __name__ == "__main__":

    app.run(host='0.0.0.0',port=5000)

