from tkinter import image_names
from flask import Flask, session, request, render_template, redirect, flash, url_for, jsonify
from models import *
from flask_migrate import *
from flask_script import Manager
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import folder_url, folder_url_user


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
    shows = Show.query.all()
    artists = User.query.filter_by(is_artist=True).all()
    users = User.query.filter_by(is_artist=False).all()
    current_time = datetime.now()
    return render_template('index.html', user=user, artists=artists, venues=venues, shows=shows, users=users, current_time=current_time)


# <-- AUTHORIZATION -->


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('re-password')
        photo = request.files['image_user']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join("static/user_images", filename))
        file_url = "static/user_images"
        result = file_url+'/'+filename
        if request.form.get('is_admin'):
            is_admin = True
        else:
            is_admin = False
        if request.form.get('is_artist'):
            is_artist = True
        else:
            is_artist = False
        print(request.form.get('is_artist'))
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
                            password=generate_password_hash(password, method='sha256'), is_admin=is_admin, image_user=result)
            db.session.add(new_user)
            db.session.commit()

            flash('Account created', category='success')
        get_user = User.query.filter_by(username=username).first()
        session['user'] = get_user.username
        return redirect(url_for('login'))
    return render_template('sign_up.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        get_user = User.query.filter_by(username=name).first()
        if get_user:
            if check_password_hash(get_user.password, password):
                session['user'] = get_user.username
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
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
    session.pop('user', None)
    return redirect(url_for('home'))


# <-- VENUES -->


@app.route('/create-venue', methods=['POST', 'GET'])
def create_venue():
    user = get_current_user()
    if request.method == 'POST':
        photo = request.files['image_venue']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join("static/images", filename))
        file_url = "static/images"
        result = file_url+'/'+filename
        new_venue = Venue(name_place=request.form.get(
            'name_venue'), address_place=request.form.get('address_venue'), image_place=result)
        db.session.add(new_venue)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_venue.html', user=user)


@app.route('/update_venue/<int:venue_id>', methods=['POST', 'GET'])
def update_venue(venue_id):
    user = get_current_user()
    venue = Venue.query.filter_by(id=venue_id).first()

    if request.method == 'POST':
        photo = request.files['image_venue']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join("static/images", filename))
        file_url = "static/images"
        result = file_url+'/'+filename
        Venue.query.filter_by(id=venue_id).update({"name_place": request.form.get(
            'name_venue'), "address_place": request.form.get('address_venue'), "image_place": result})
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('update_venue.html', user=user, venue=venue)


@app.route('/delete_venue/<int:venue_id>', methods=['POST', 'GET'])
def delete_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    for show in venue.shows:
        db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
    return redirect(url_for('home'))


@ app.route('/venue_page/<int:venue_id>')
def venue_page(venue_id):
    user = get_current_user()
    venue = Venue.query.filter_by(id=venue_id).first()
    return render_template('venue_page.html', venue=venue, user=user)


@ app.route('/check_venue/<int:venue_id>', methods=['POST', 'GET'])
def check_venue(venue_id):
    user = get_current_user()
    venue = Venue.query.filter_by(id=venue_id).first()
    if request.method == "POST":
        check_time = request.form.get('check-time')
        for show in venue.shows:
            if show.start_time <= check_time <= show.finish_time:
                flash('Sorry! It is busy', category='error')
            else:
                flash('It is free. You can keep it busy', category='success')
                return redirect(url_for('venue_page', venue_id=venue_id))
    return render_template('venue_page.html', venue=venue, user=user)


@ app.route('/check_date/<int:venue_id>', methods=['POST'])
def check_date(venue_id):
    object = {}
    object['found'] = False
    time_to_check = request.get_json()['time_entered']
    time_to_check_to_date = None
    if time_to_check:
        time_to_check_to_date = datetime.strptime(
            time_to_check, '%Y-%m-%dT%H:%M')
    else:
        object['found'] = 'None'
    print(time_to_check_to_date)
    venue = Venue.query.filter_by(id=venue_id).first()
    if time_to_check_to_date:
        for show in venue.shows:
            show_start = show.start_time
            show_finish = show.finish_time

            if show_start.replace(tzinfo=None) <= time_to_check_to_date.replace(tzinfo=None) <= show_finish.replace(tzinfo=None):
                object['found'] = True

    return jsonify(object)


# <-- SHOWS -->


@ app.route('/create-concert', methods=['POST', 'GET'])
def create_concert():
    user = get_current_user()
    venues = Venue.query.all()
    # artist = User.query.filter_by(id=artist_id).first()
    if request.method == 'POST':
        photo = request.files['image_show']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join("static/images", filename))
        file_url = "static/images"
        result = file_url+'/'+filename
        if request.form.get('time-start') < request.form.get('time-finish'):
            new_concert = Show(name_show=request.form.get(
                'name_show'), start_time=request.form.get('time-start'), finish_time=request.form.get('time-finish'), venue_id=request.form.get('select-venue'), image_show=result)
            db.session.add(new_concert)
            db.session.commit()
            # User.query.filter_by(id=artist_id).update(
            #     {'show_id': new_concert.id})
            # db.session.commit()
        else:
            flash('Finish time must be greater than start time', category='error')
            return redirect(url_for('create_concert'))
        return redirect(url_for('home'))
    return render_template('new_concert.html', venues=venues, user=user)


@ app.route('/update_concert/<int:show_id>', methods=['POST', 'GET'])
def update_show(show_id):
    user = get_current_user()
    venues = Venue.query.all()
    show = Show.query.filter_by(id=show_id).first()
    # artist = User.query.filter_by(id=artist_id).first()
    if request.method == 'POST':
        photo = request.files['image_show']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join("static/images", filename))
        file_url = "static/images"
        result = file_url+'/'+filename
        if request.form.get('time-start') < request.form.get('time-finish'):
            Show.query.filter_by(id=show_id).update({'name_show': request.form.get(
                'name_show'), "start_time": request.form.get('time-start'), "finish_time": request.form.get('time-finish'), "venue_id": request.form.get('select-venue'), "image_show": result})
            db.session.commit()
            # User.query.filter_by(id=artist_id).update(
            #     {'show_id': new_concert.id})
            # db.session.commit()
        else:
            flash('Finish time must be greater than start time', category='error')
            return redirect(url_for('create_concert'))
        return redirect(url_for('home'))
    return render_template('update_concert.html', venues=venues, user=user, show=show)


@app.route('/delete_show/<int:show_id>', methods=['POST', 'GET'])
def delete_show(show_id):
    show = Show.query.filter_by(id=show_id).first()
    db.session.delete(show)
    db.session.commit()
    return redirect(url_for('home'))


@ app.route('/concert_page/<int:concert_id>/<int:venue_id>')
def concert_page(concert_id, venue_id):
    user = get_current_user()
    users = User.query.filter_by(is_artist=True).all()
    concert = Show.query.filter_by(id=concert_id).first()
    venue = Venue.query.filter_by(id=venue_id).first()
    date_to_str_start = concert.start_time.strftime("%d.%m.%Y %H:%M")
    date_to_str_finish = concert.finish_time.strftime("%d.%m.%Y %H:%M")
    return render_template('concert_page.html', concert=concert, user=user, venue=venue, date_to_str_start=date_to_str_start, date_to_str_finish=date_to_str_finish, users=users)


@ app.route('/add_artist_to_show/<int:show_id>', methods=['POST', 'GET'])
def add_artist_to_show(show_id):
    if request.method == 'POST':
        show = Show.query.filter_by(id=show_id).first()
        users_true = User.query.filter_by(chosen_to_show=True).all()
        for worker in users_true:
            show.users.append(worker)
            db.session.commit()
        for worker in users_true:
            worker.chosen_to_show = False
            db.session.commit()
        return redirect(url_for('concert_page', concert_id=show_id, venue_id=show.venue_id))
    # return render_template('concert_page.html', user=user, users=users)


@ app.route('/delete_show_artist/<int:show_id>/<int:artist_id>/<int:venue_id>', methods=['POST', 'GET'])
def delete_show_artist(show_id, artist_id, venue_id):
    artist = User.query.filter_by(id=artist_id).first()
    show = Show.query.filter_by(id=show_id).first()
    for artist in show.users:
        if artist.id == artist_id:
            show.users.remove(artist)
            db.session.commit()
    return redirect(url_for('concert_page', concert_id=show_id, venue_id=venue_id))


@ app.route('/set_artist/<int:artist_id>', methods=['POST'])
def set_artist(artist_id):
    complete = request.get_json()['user_checkbox']
    user_check = User.query.get(artist_id)
    user_check.chosen_to_show = complete
    db.session.commit()
    return True


# <-- ARTISTS -->

@ app.route('/check_date_user/<int:user_id>', methods=['POST'])
def check_date_user(user_id):
    object = {}
    object['found'] = False
    time_to_check = request.get_json()['time_entered']
    if time_to_check:
        time_to_check_to_date = datetime.strptime(
            time_to_check, '%Y-%m-%dT%H:%M')
    else:
        object['found'] = 'None'
    user = User.query.filter_by(id=user_id).first()
    shows = Show.query.all()
    for show in shows:
        if show.id == user.show_id:
            show_start = show.start_time
            show_finish = show.finish_time

            if show_start.replace(tzinfo=None) <= time_to_check_to_date.replace(tzinfo=None) <= show_finish.replace(tzinfo=None):
                object['found'] = True

    return jsonify(object)


@ app.route('/add_artist', methods=['POST', 'GET'])
def add_artist():
    user = get_current_user()
    users = User.query.all()
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('re-password')
        photo = request.files['image_user']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join("static/user_images", filename))
        file_url = "static/user_images"
        result = file_url+'/'+filename
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
                            password=generate_password_hash(password, method='sha256'), is_artist=True, image_user=result)
            db.session.add(new_user)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_artist.html', users=users, user=user)


@ app.route('/update_artist/<int:artist_id>', methods=['POST', 'GET'])
def update_artist(artist_id):
    user = get_current_user()
    users = User.query.all()
    artist = User.query.filter_by(id=artist_id).first()
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('re-password')
        photo = request.files['image_user']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join("static/user_images", filename))
        file_url = "static/user_images"
        result = file_url+'/'+filename
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
            User.query.filter_by(id=artist_id).update({'email': email, 'username': username,
                                                       'password': generate_password_hash(password, method='sha256'), 'is_artist': True, 'image_user': result})
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('update_artist.html', users=users, user=user, artist=artist)


@app.route('/delete_artist/<int:artist_id>', methods=['POST', 'GET'])
def delete_artist(artist_id):
    artist = User.query.filter_by(id=artist_id).first()
    db.session.delete(artist)
    db.session.commit()
    return redirect(url_for('home'))


@ app.route('/artist_page/<int:user_id>')
def artist_page(user_id):
    user = get_current_user()
    artist = User.query.filter_by(id=user_id).first()
    shows = Show.query.all()
    return render_template('artist_page.html', artist=artist, user=user, shows=shows)


manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
