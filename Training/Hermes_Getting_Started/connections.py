from flask import Flask
from flaskext.mysql import MySQL
app = Flask(__name__)

mysql=MySQL()

# Database
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '' # Enter correct password
app.config['MYSQL_DATABASE_DB'] = 'myBusiness'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)
