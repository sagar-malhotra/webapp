from operator import truediv
from queue import Empty
from urllib.request import HTTPBasicAuthHandler
import pymysql
from app2 import app
from db import mysql
from flask import jsonify
from flask import flash, request
import datetime
import bcrypt
import logging
import base64
from flask_httpauth import HTTPBasicAuth 

logging.basicConfig(level=logging.DEBUG)

auth= HTTPBasicAuth()
salt = b'$2b$12$mczJI..aWJ5wB0IRNGksIOuBYgsKdJE.902cFpnYsWa14NtQCvcGm' 
def get_hashed_password(password):

	passw = password.encode('utf-8')
	
	return bcrypt.hashpw(passw, salt)



@app.route('/add', methods=['POST'])
def add_user():
	conn = None
	cursor = None
	now = datetime.datetime.now()
	try:
		_json = request.json
		_email = _json['Email']
		_password = _json['Password']
		_fname = _json['First_Name']
		_lname = _json['Last_Name']


		if _fname and _lname and _email and _password and request.method == 'POST':

			_hashed_password = get_hashed_password(_password)
			
			sql = "INSERT INTO tbl_user(user_email, user_password, user_fname, user_lname, account_created ) VALUES(%s, %s, %s, %s, %s)"
			data = (_email, _hashed_password, _fname, _lname, str(now))
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			cursor.close()
			cursor =conn.cursor(pymysql.cursors.DictCursor)
			cursor.execute("SELECT user_id Id, user_email Email,  user_fname First_Name,  user_lname Last_Name FROM tbl_user WHERE user_email=%s", _email)
			row = cursor.fetchone()

			resp = jsonify(row)
			resp.status_code = 200
			return resp
			
			# resp = jsonify(Description='User added successfully!', Code=201)
			# resp.status_code = 201
			# return resp
		else:
			return not_found()
	except Exception as e:
		resp = jsonify(Description='Bad Request', Code=400)
		resp.status_code = 400
		return resp
	finally:
		cursor.close() 
		conn.close()


@app.route('/update', methods=['PUT'])
def update_user():

	conn = None
	cursor = None
	now = datetime.datetime.now()
	try:
		_json = request.json
		_email = _json['Email']
		_password = _json['Password']	
		_fname = _json['First_Name']
		_lname = _json['Last_Name']
		
		if _email and request.method == 'PUT':
			conn = mysql.connect()
			cursor =conn.cursor(pymysql.cursors.DictCursor)
			cursor.execute("SELECT user_email Email, user_password Password FROM tbl_user WHERE user_email=%s", _email)	
			c = cursor.fetchone()
			if (c is None):
				
				cursor.close()
				resp = jsonify(Description="Bad Request", Code=400)
				resp.status_code=400
				return resp
			else:
				
				cursor.close()
				
				auth1 = str(request.headers['Authorization'])[6:]
				auth_temp = base64.b64decode(auth1)
			
				temp= str(auth_temp).split(":")
				u_name=str(temp[0])[2:]
				p = str(temp[1])			
				hash_p = get_hashed_password(p[:-1])
			
				v_auth= c.get('Password')
				user_auth= c.get('Email')
				if(str(hash_p)[2:].replace('\'','')==v_auth and user_auth==u_name):

					_hashed_password = get_hashed_password(_password)
					sql = "UPDATE tbl_user SET user_password=%s, user_fname=%s , user_lname =%s, account_updated=%s  WHERE user_email=%s"
					data = (_hashed_password, _fname, _lname,str(now), _email,)
					conn = mysql.connect()
					cursor = conn.cursor()
					cursor.execute(sql, data)
					conn.commit()
					resp = jsonify('User updated successfully!')
					resp.status_code = 200
					return resp
				else:
					conn = mysql.connect()
					cursor = conn.cursor()
					resp = jsonify(Error="Unauthorized User",Code=400)
					resp.status_code = 400
					return resp

		else:
			return not_found()
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/user/<int:id>')
def user(id):
	conn = None
	cursor = None
	try:

		conn = mysql.connect()
		cursor =conn.cursor(pymysql.cursors.DictCursor)
		#cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT user_email Email, user_password Password FROM tbl_user WHERE user_id=%s", id)
		
		c =cursor.fetchone()
		if (c is None):
			
			cursor.close()
			resp = jsonify(Description="Bad Request- ID not found", Code=400)
			resp.status_code=400
			return resp
		else:

			cursor.close()
			
			auth1 = str(request.headers['Authorization'])[6:]
			auth_temp = base64.b64decode(auth1)
			temp= str(auth_temp).split(":")
			u_name=str(temp[0])[2:]
			p = str(temp[1])			
			hash_p = get_hashed_password(p[:-1])
			
			v_auth= c.get('Password')
			user_auth= c.get('Email')
			if(str(hash_p)[2:].replace('\'','')==v_auth and user_auth==u_name):
				cursor =conn.cursor(pymysql.cursors.DictCursor)
				cursor.execute("SELECT user_id Id, user_email Email,  user_fname First_Name,  user_lname Last_Name, account_created Account_Created, account_updated Account_Updated FROM tbl_user WHERE user_id=%s", id)
				row = cursor.fetchone()
				resp = jsonify(row)
				resp.status_code = 200
				return resp
			else:
				
				resp = jsonify(Description="Unauthorized User",Code=400)
				resp.status_code = 400
				return resp

	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

		
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 400,
        'message': 'Bad Request',
    }
    resp = jsonify(message)
    resp.status_code = 400

    return resp
	
if __name__ == "__main__":
    app.run()