# Assignment 2 WebApp
This is a simple python based API that takes user details from user in Json format and stores it in the MySql database when called.

The API Allows to Add User, Updated User Details and View User Details.

This API Uses Basic Auth for authenticating the user identyty for retieve and update functions.


Please ensure you have python installed in your system to build and deploy this API.

To download python you can visit  https://www.python.org/downloads/ 

Once python is installed, run the following command to install FLASK Libraries
- pip install Flask  (Flask Dependencies)
- pip install PyMySQL (Python Mysql connector)
- pip install flask-mysql (Flask mysql libraries)
- pip install flask_table (Flask Relational tables libraries)
- pip install py-bcrypt (bcrypt hashing libraries)

Ensure you have Mysql database installed and add the database details to the db.py which inclus Database user, password, name and url.

Create a database name tbl_user with the following syntax in the database.

CREATE TABLE `tbl_user` (
  `user_id` bigint COLLATE utf8mb4_unicode_ci NOT NULL AUTO_INCREMENT,
  `user_email` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_password` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_fname` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_lname` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `account_created` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `account_updated` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

Run the application using the command
- Python ./routes.py

Check the url on which the application is running
Use Postman to hit the API and validate the response. 
 
Run the unit test using command

- Python ./tests.py



