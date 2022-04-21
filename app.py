from flask import Flask, session, request, render_template, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from models import *
from flask_migrate import *
from flask_script import Manager
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import folder_url


app = Flask(__name__)
app.config.from_object('config')
db = setup(app)


def get_current_user():
    user_query = None
    if 'user' in session:
        user = session['user']
        user = User.query.filter_by(username=user).first()
        user_query = user
    return user_query


@app.route('/')
def home():
    user = get_current_user()
    venues = Venue.query.all()
    return render_template('index.html', user=user, venues=venues)


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('re-password')

        if len(email) <= 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(username) <= 2:
            flash(
                'Username must be greater than 2 characters', category='error')
        elif len(password) <= 4:
            flash('Password must be greater than 4 characters', category='error')
        elif password != password2:
            flash('Password do not match', category='error')
        else:
            new_user = User(email=email, username=username,
                            password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            flash('Account created', category='success')
        get_user = User.query.filter_by(username=username).first()
        session['user'] = get_user.username
        return redirect(url_for('home'))
    return render_template('sign_up.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # if len(email) <= 4:
        #     flash('Email must be greater than 4 characters', category='error')
        # elif len(firstname)<=2 and len(lastname)<2:
        #     flash('Firstname and Lastname must be greater than 2 characters', category='error')
        # elif len(password) <= 4:
        #     flash('Password must be greater than 4 characters', category='error')
        # elif password != password2:
        #     flash('Password do not match', category='error')
        # else:
        #     flash('Account created', category='success')

    return render_template('login.html')


@app.route('/logout')
def logout():
    return 'Logout'


@app.route('/create-venue', methods=['POST', 'GET'])
def create_venue():
    if request.method == 'POST':
        photo = request.files['image_venue']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOADED_FOLDER'], filename))
        file_url = folder_url()
        result = file_url+'/'+filename
        new_venue = Venue(name_place=request.form.get(
            'name_venue'), address_place=request.form.get('name_venue'), image_place=result)
        db.session.add(new_venue)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_venue.html')


manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
