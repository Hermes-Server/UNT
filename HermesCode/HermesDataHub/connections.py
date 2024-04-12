from flask import Flask
from flaskext.mysql import MySQL
app = Flask(__name__)

mysql=MySQL()

# Database
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = '0123456789' # Enter correct password
app.config['MYSQL_DATABASE_DB'] = 'unt'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)
