from flask import Flask, render_template, redirect, url_for, flash, session
from extensions import db  # db instance created in extensions.py
# from forms import RegistrationForm, LoginForm, ProfileForm
import os
from flask import current_app, request, flash, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename
from forms import *
from models import User, Banner
from flask import request

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session and flash

# Replace these values with your phpMyAdmin/MySQL details
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flaskproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db with flask app

@app.route('/')
def home():
    return 'Home Page Loaded Successfully!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()

        if existing_user:
            flash('Username or email already exists. Please use a different one.')
            return redirect(url_for('register'))

        user = User(
            username=form.username.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            nickname=form.nickname.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('User registered successfully.')
        return redirect(url_for('login'))
    else:
        if form.is_submitted():
            print("Form errors:", form.errors)
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # User authenticated, set session variables here
            session['superuser'] = True
            session['user_name'] = user.username  # Store username in session
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data, logging the user out
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if not session.get('superuser'):
        flash('Access denied.')
        return redirect(url_for('login'))
    # Pass username stored in session during login
    return render_template('dashboard.html', user_name=session.get('user_name', 'User'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_name = session.get('user_name', 'User')
    if not session.get('superuser'):
        flash('Access denied.')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session.get('user_name')).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))

    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        # Update username too
        user.username = form.username.data
        user.email = form.email.data
        user.phone_number = form.phone_number.data
        user.nickname = form.nickname.data

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()

        # Update session username if changed
        session['user_name'] = user.username

        flash("Profile updated successfully!")
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form, user_name=user_name)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not session.get('superuser'):
        flash('Access denied.')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session.get('user_name')).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))

    form = SettingsForm()

    if form.validate_on_submit():
        if form.new_password.data:
            user.set_password(form.new_password.data)
        # Save email notification preference in your user model if available
        # user.email_notifications = form.email_notifications.data
        
        db.session.commit()
        flash('Settings updated!')
        return redirect(url_for('settings'))

    # Prepopulate form from user data if needed
    # form.email_notifications.data = user.email_notifications if hasattr(user, 'email_notifications') else False

    return render_template('settings.html', form=form)




@app.route('/add_banner', methods=['GET', 'POST'])
def add_banner():
    if not session.get('superuser'):
        flash('Access denied.')
        return redirect(url_for('login'))

    form = BannerForm()
    if form.validate_on_submit():
        # Handle image upload
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, filename)
        image_file.save(image_path)

        # Create absolute URL for saved image
        image_url = url_for('static', filename='uploads/' + filename, _external=True)

        # Save banner to database
        banner = Banner(
            image_url=image_url,  # Absolute image URL
            alt_text=form.alt_text.data,
            read_more_link=form.read_more_link.data,
            heading=form.heading.data,
            sub_heading=form.sub_heading.data
        )
        db.session.add(banner)
        db.session.commit()
        flash('Banner added successfully!')
        return redirect(url_for('add_banner'))

    return render_template('banner.html', form=form)

@app.route('/banner_list')
def banner_list():
    if not session.get('superuser'):
        flash('Access denied.')
        return redirect(url_for('login'))

    banners = Banner.query.all()
    return render_template('banner_list.html', banners=banners)


# from werkzeug.utils import secure_filename
# import os
# from flask import current_app

@app.route('/update_banner/<int:banner_id>', methods=['GET', 'POST'])
def update_banner(banner_id):
    if not session.get('superuser'):
        flash('Access denied.')
        return redirect(url_for('login'))
    
    banner = Banner.query.get_or_404(banner_id)
    form = BannerForm(obj=banner)
    
    if form.validate_on_submit():
        # Handle image upload only if a new image is provided
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            
            # Update image url in database
            banner.image_url = url_for('static', filename='uploads/' + filename, _external=True)

        # Update other fields
        banner.alt_text = form.alt_text.data
        banner.read_more_link = form.read_more_link.data
        banner.heading = form.heading.data
        banner.sub_heading = form.sub_heading.data
        
        db.session.commit()
        flash('Banner updated successfully!')
        return redirect(url_for('banner_list'))

    return render_template('update_banner.html', form=form, banner=banner)




# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This creates the Banner table if not exists
    app.run(debug=True)
