
import base64
from distutils.log import error
import email
import errno
from http.client import BAD_REQUEST
from multiprocessing.connection import wait
from flask import abort, request
import requests
from Assignment_2 import app
from Database import SqlAlchemy as mysql
from flask import jsonify
import pymysql

#from werkzeug.security import generate_password_hash
from datetime import datetime

import bcrypt
import logging
# logging.basicConfig(level=logging.DEBUG)

s =b'$2b$12$5bLd8.tAyVOYX66Y2KLNROtA86OappyUFvMtpSYsMDGnH2z1HNnUO'

@app.route('/createuser', methods=['POST'])
def create_user():
	
	#dbcon =None
	csr =None
	
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
			# #dbcon = mysql.connect()
			csr = mysql.cursor()
			
			# # execute the query
			csr.execute(query, field)
			
			mysql.commit()
			
			# rows = csr.fetchone()
			csr.close()	
			
			csr = mysql.cursor()
			
			query = "SELECT u_id,u_email,u_fname,u_lname from tbl_create_user where u_email= %s"
			field = (email,)
			csr.execute(query, field)
			
			data=csr.fetchone()
		
			result = jsonify(data)
			
			# result = jsonify('User added successfully!',201)
			result.status_code = 201
			
			return result
		else:
			#dbcon = mysql.connect()
			csr = mysql.cursor()
			return not_found()
	# except mysql.connector.Error:
	# 	print("error duplicacy")
	except Exception as e:
		# print(e)
		db_error=True		
		# dbcon = mysql.connect()
		# csr = dbcon.cursor()

	finally:
		#dbcon = mysql.connect()
		csr = mysql.cursor()
		csr.close() 
		#dbcon.close()

	if db_error:
		# print("duplicate error")
		result=jsonify(Error="BAD_REQUEST", Code = 400  )	
		result.status=400
		
		# return jsonify((400, 'Record Not Found')) 
		# result.status_code="400 BAD_REQUEST"
		return result
		
# @app.route('/userdetails',methods=['GET'])
# def users():
@app.route('/userdetails/<int:Id>')
def user(Id):	
	#dbcon = None
	csr = None
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
					query="SELECT u_id,u_email,u_fname,u_lname,acc_created,acc_updated from tbl_create_user where u_id=%s"
					field=(Id,)
					csr.execute(query,field)
					# field = (email)
					exist = csr.fetchone()
					if exist is None:
						
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
					return result
				else:
					result=jsonify("Bad_Request",400)
					result.status_code=400
					return result
	except Exception :
		db_error=True
		# result=jsonify(Error="Bad_Request-No details found", Code = 400  )	
		# result.status=400
		# result.status_code=400
		# print(e)
	finally:
		
		csr.close() 
		#dbcon.close()
	if db_error:
		# print("duplicate error")
		result=jsonify(Error="BAD_REQUEST", Code = 400  )	
		result.status_code=400
		
		# return jsonify((400, 'Record Not Found')) 
		# result.status_code="400 BAD_REQUEST"
		return result

@app.route("/healthz")

def myname():
    return jsonify({"Application is healthy": "200"})

@app.route('/update', methods=['PUT'])
def update_user():
	
	#dbcon = None
	csr = None
	
	try:
		
		js = request.json
		email =js['email']
		password =js['password']
		fname =js['fname']
		lname=js['lname']
		
		# datetime object containing current date and time
		now = datetime.now()

		# dd/mm/YY H:M:S
		u_update = now.strftime("%d/%m/%Y %H:%M:%S")	
		
		# validate the received values
		if email and request.method == 'PUT':
			
			#dbcon=mysql.connect()
			csr=mysql.cursor()
			query="Select u_email em, u_password pd from tbl_create_user where u_email=%s"
			field=(email,)
			csr.execute(query,field)

			rec=csr.fetchone()

			if(rec is None):
				
				csr.close()
				result=jsonify("Bad_Request",400)
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
				print(rec)
				print(type(rec))
				db_pwd=rec[1]
				db_uname=rec[0]
				
				if((str(hash_pwd)[2:].replace('\'','')==db_pwd) and (auth_uname==db_uname) ):
					print("matched")
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
						raise logging.exception
					# 	print("csr is none")
					# exist = csr.fetchone()
					# if exist is not None:
										
					result = jsonify('User updated successfully!')
					result.status_code = 200
					return result

				else:
					#dbcon = mysql.connect()
					csr = mysql.cursor()
					result=jsonify("Unauthorized User",400)
					result.status_code = 400
					return result
			
	except Exception as e:
		# print(e)
		#dbcon = mysql.connect()
		csr = mysql.cursor()
		result=jsonify(Error="Bad_Request", Code = 400  )	
		
		result.status_code=400
		return result
		# # resp = jsonify("User can't be updated!")
		# # resp.status_code = 404
		# # return result
		# # print(e)
	finally:
		csr.close() 
		#dbcon.close()
		

		
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
	
    app.run()
	