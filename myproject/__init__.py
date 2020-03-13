import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES

# Create a login manager object
login_manager = LoginManager()

app = Flask(__name__)
photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'images'
# Often people will also separate these into a separate config.py file
app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
configure_uploads(app, photos)
Migrate(app,db)

# We can now pass in our app to the login manager
login_manager.init_app(app)

# Tell users what view to go to when they need to login.
login_manager.login_view = "login"