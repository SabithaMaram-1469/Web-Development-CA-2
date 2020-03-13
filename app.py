from flask import render_template, redirect, request, url_for, flash,abort
from flask_login import login_user,login_required,logout_user, UserMixin
from myproject.forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField, SelectField
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES


# Tell users what view to go to when they need to login.

# Create a login manager object


app = Flask(__name__)


app.config['UPLOADED_PHOTOS_DEST'] = 'images'
# Often people will also separate these into a separate config.py file
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
photos = UploadSet('photos', IMAGES)
db = SQLAlchemy(app)
configure_uploads(app, photos)
Migrate(app,db)
login_manager = LoginManager()
# We can now pass in our app to the login manager
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):

    # Create a table in the database
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Integer) #in cents
    stock = db.Column(db.Integer)
    description = db.Column(db.String(500))
    image = db.Column(db.String(100))

class AddProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')
    stock = IntegerField('Stock')
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])

class DeleteProduct(FlaskForm):
    name = StringField('Name')

class UpdateProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/products',methods=['GET','POST'])
def products():
    products = Product.query.all()
    db.session.commit()
    return render_template('products.html', products=products)

@app.route('/product/<id>')
def product(id):
    product = Product.query.filter_by(id=id).first()
    return render_template('view-product.html', product=product)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddProduct()

    if form.validate_on_submit():
        image_url = photos.url(photos.save(form.image.data))
        new_product = Product(name=form.name.data, price=form.price.data, stock=form.stock.data, description=form.description.data, image=image_url)
        print(image_url)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('products'))

    return render_template('add-product.html', form=form)



@app.route('/admin/delete', methods=['GET', 'POST'])
@login_required
def delete():
    form = DeleteProduct()

    if form.validate_on_submit():

        del_product = Product.query.filter_by(name=form.name.data).first()
        db.session.delete(del_product)
        db.session.commit()

        return redirect(url_for('products'))

    return render_template('delete-product.html', form=form)

@app.route('/admin/update', methods=['GET', 'POST'])
@login_required
def update():
    form = UpdateProduct()

    if form.validate_on_submit():

        update_product = Product.query.filter_by(name=form.name.data).first()
        update_product.price=form.price.data
        print(update_product.price)

        db.session.commit()

        return redirect(url_for('products'))

    return render_template('update-product.html', form=form)






@app.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome_user.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()
        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            #Log in the user
            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0]=='/':
                next = url_for('welcome_user')

            return redirect(next)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
