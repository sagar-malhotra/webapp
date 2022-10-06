from app2 import app
from flaskext.mysql import MySQL

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root1'
app.config['MYSQL_DATABASE_DB'] = 'assignment2'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)