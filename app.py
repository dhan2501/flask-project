from flask import Flask, render_template, redirect, url_for, flash, session
from extensions import db  # db instance created in extensions.py
# from forms import RegistrationForm, LoginForm, ProfileForm
import os
from flask import current_app, request, flash, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename
from forms import *
from models import *
from flask import request
from flask_mail import Mail, Message
from email_validator import validate_email, EmailNotValidError




app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session and flash


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='dhananjaygupta2501@gmail.com',          # your Gmail
    MAIL_PASSWORD='sant iekm bgwe wgyw',    # App password, not your Gmail password
    MAIL_DEFAULT_SENDER='dhananjaygupta2501@gmail.com'
)
mail = Mail(app)

# Replace these values with your phpMyAdmin/MySQL details
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flaskproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db with flask app



@app.route('/')
def home():
    # Query single main banner (for Hero section)
    banner_main = Banner.query.first()  # Or select by type/flag
    
    # Query other banners for Popular Destination
    banners = Banner.query.all()

    return render_template('home.html', banner_main=banner_main, banners=banners)


@app.route('/about')
def about():
    return render_template('frontend/about.html')


@app.route('/blog')
def blog():
    return render_template('frontend/blog.html')


@app.route('/contact')
def contact():
    return render_template('frontend/contact.html')


@app.context_processor
def inject_user():
    user_name = session.get('user_name', 'User')
    user = None
    if user_name:
        user = User.query.filter_by(username=user_name).first()
    return dict(user_name=user_name, user=user)



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
        user.username = form.username.data
        user.email = form.email.data
        user.phone_number = form.phone_number.data
        user.nickname = form.nickname.data

        if form.password.data:
            user.set_password(form.password.data)

        # Handle avatar file upload
        if form.avatar.data:
            avatar_file = form.avatar.data
            filename = secure_filename(avatar_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            avatar_file.save(filepath)

            # Save relative URL path to avatar_url
            user.avatar_url = url_for('static', filename=f'uploads/avatars/{filename}')

        db.session.commit()

        # Update session username if changed
        session['user_name'] = user.username

        flash("Profile updated successfully!")
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form, user_name=user_name, user=user)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user_name = session.get('user_name', 'User')
    if not session.get('superuser'):
        flash('Access denied.')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session.get('user_name')).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))

    form = SettingsForm()

    if form.validate_on_submit():
        # Validate old password before allowing change
        if not user.check_password(form.old_password.data):
            flash('Old password is incorrect.')
            return redirect(url_for('settings'))

        if form.new_password.data:
            user.set_password(form.new_password.data)

        # Save email notification preference if your user model has this field
        # user.email_notifications = form.email_notifications.data

        db.session.commit()
        flash('Settings updated!')
        return redirect(url_for('settings'))

    # Prepopulate email_notifications field if applicable
    # form.email_notifications.data = getattr(user, 'email_notifications', False)

    return render_template('settings.html', form=form, user_name=user_name)



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

@app.route('/blog-list')
def blog_list():
    if not session.get('superuser'):
        flash('Access denied.')
        return redirect(url_for('login'))
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog_list.html', blogs=blogs)


# @app.route('/add-category', methods=['GET', 'POST'])
# def add_category():
#     if request.method == 'POST':
#         name = request.form['name']
#         description = request.form.get('description', '')
#         category = BlogCategory(name=name, description=description)
#         db.session.add(category)
#         db.session.commit()
#         flash('Category added!')
#         return redirect(url_for('add_category'))
#     return render_template('add_category.html')

@app.route('/category/<int:category_id>')
def blogs_by_category(category_id):
    category = BlogCategory.query.get_or_404(category_id)
    blogs = Blog.query.filter_by(category_id=category.id).all()
    return render_template('blog_list.html', blogs=blogs, category=category)

@app.route('/blog/add-category', methods=['GET', 'POST'],  endpoint='add_category')
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = BlogCategory(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!')
        return redirect(url_for('category_list'))
    return render_template('add_category.html', form=form)

@app.route('/blog/category-list')
def category_list():
    categories = db.session.query(
        BlogCategory,
        db.func.count(Blog.id).label('blog_count')
    ).outerjoin(Blog).group_by(BlogCategory.id).all()
    return render_template('category_list.html', categories=categories)


@app.route('/blog/category/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = BlogCategory.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Category updated successfully!')
        return redirect(url_for('category_list'))
    return render_template('edit_category.html', form=form)



@app.route('/blog/add', methods=['GET', 'POST'])
def add_blog():
    form = BlogForm()
    
    # Load categories for select options
    categories = BlogCategory.query.order_by(BlogCategory.name).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        image_file = form.image.data
        filename = None
        if image_file:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            image_url = url_for('static', filename='uploads/' + filename, _external=True)
        else:
            image_url = None

        blog = Blog(
            image_url=image_url or "",
            alt_text=form.alt_text.data,
            short_description=form.short_description.data,
            description=form.description.data,
            meta_title=form.meta_title.data,
            meta_description=form.meta_description.data,
            meta_keywords=form.meta_keywords.data,
            twitter_title=form.twitter_title.data,
            twitter_description=form.twitter_description.data,
            twitter_keywords=form.twitter_keywords.data,
            category_id=form.category_id.data,  # save selected category
            schema_data=None
        )
        db.session.add(blog)
        db.session.commit()
        flash('Blog added successfully!')
        return redirect(url_for('blog_list'))
    
    return render_template('add_blog.html', form=form)

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog_detail.html', blog=blog)



@app.route('/blog/edit/<int:blog_id>', endpoint='edit_blog', methods=['GET', 'POST'])
def update_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)  # Fetch blog or 404 if not found
    form = BlogForm(obj=blog)  # Populate form with blog data

    if form.validate_on_submit():
        image_file = form.image.data
        if image_file:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            blog.image_url = url_for('static', filename='uploads/' + filename, _external=True)
        # Update blog fields from form data
        blog.alt_text = form.alt_text.data
        blog.short_description = form.short_description.data
        blog.description = form.description.data
        blog.meta_title = form.meta_title.data
        blog.meta_description = form.meta_description.data
        blog.meta_keywords = form.meta_keywords.data
        blog.twitter_title = form.twitter_title.data
        blog.twitter_description = form.twitter_description.data
        blog.twitter_keywords = form.twitter_keywords.data

        # Optionally handle schema_data if in form
        # blog.schema_data = ...

        db.session.commit()
        flash('Blog updated successfully!')
        return redirect(url_for('blog_list'))

    return render_template('edit_blog.html', form=form, blog=blog)


@app.route('/contact-us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Email to site owner
        # msg_to_admin = Message(
        #     subject=f"New Contact Form Submission from {name}",
        #     recipients=['dhananjaygupta2501@gmail.com'],  # Your email
        #     body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
        # )

        msg_to_admin = Message(
            subject=f"New Contact Form Submission from {name}",
            recipients=['dhananjaygupta2501@gmail.com'],
            html=f"""
            <html>
            <body style="font-family: Arial, sans-serif; background:#f9f9f9; padding:20px;">
            <div style="max-width:600px; margin:auto; background:#fff; padding:20px; border:1px solid #ddd; border-radius:6px;">
                <h2 style="color:#1a73e8; text-align:center;">New Contact Form Submission</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Message:</strong></p>
                <blockquote style="background:#f1f1f1; border-left:4px solid #1a73e8; padding:10px 15px; font-style:italic; color:#555; white-space: pre-wrap;">{message}</blockquote>
            </div>
            </body>
            </html>
            """
        )


        # Thank you email to user
        # msg_to_user = Message(
        #     subject="Thank you for contacting us",
        #     recipients=[email],  # User’s email
        #     body=f"Dear {name},\n\nThank you for reaching out to us. We have received your message and will get back to you shortly.\n\nBest regards,\nManaging Director"
        # )

        msg_to_user = Message(
            subject="Thank you for contacting us",
            recipients=[email],  # User's email
            html=f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8" />
            <title>Thank You</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; }}
                .container {{ max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h2 {{ color: #2e8b57; }}
                p {{ font-size: 16px; color: #333; }}
            </style>
            </head>
            <body>
            <div class="container">
                <h2>Thank You, {name}!</h2>
                <p>We have received your message and will get back to you shortly.</p>
                <p><strong>Your Message:</strong></p>
                <blockquote style="background:#f1f1f1; padding:10px; border-left: 5px solid #2e8b57;">{message}</blockquote>
                <p>Best regards,<br/>Managing Director</p>
            </div>
            </body>
            </html>
            """
        )


        try:
            mail.send(msg_to_admin)
            mail.send(msg_to_user)
            flash('Message sent successfully! A confirmation email has been sent to your email.')
        except Exception as e:
            flash('Failed to send message. Please try again later.')
            print(f"Error sending mail: {e}")

        return redirect(url_for('contact_us'))

    # Render the contact form on GET
    return render_template('frontend/contact.html')


@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/contact-support', methods=['GET', 'POST'])
def contact_support():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('All fields are required.', 'danger')
            return redirect(url_for('contact_support'))
        
        # Validate email
        try:
            validated_email = validate_email(email).email
        except EmailNotValidError as e:
            flash(str(e), 'danger')
            return redirect(url_for('contact_support'))

        # Send thank you email to user
        user_msg = Message(
            subject="Thank you for contacting support",
            recipients=[validated_email],
            body=f"Hi {name},\n\nThank you for reaching out! We received your message and will get back to you shortly.\n\nYour message:\n{message}\n\nBest regards,\nSupport Team"
        )
        mail.send(user_msg)

        # Send notification email to admin
        admin_email = 'dhananjaygupta2501@gmail.com'  # replace with your admin email
        admin_msg = Message(
            subject="New Support Request Received",
            recipients=[admin_email],
            body=f"Support request from {name} ({validated_email}):\n\n{message}"
        )
        mail.send(admin_msg)

        flash('Thank you for contacting support! Confirmation sent to your email.', 'success')
        return redirect(url_for('contact_support'))

    return render_template('contact_support.html')





# Category Routes
from sqlalchemy import func
@app.context_processor
def inject_categories():
    categories_with_counts = (
        db.session.query(
            Category,
            func.count(Product.id).label('product_count')
        )
        .outerjoin(Category.products)
        .group_by(Category.id)
        .all()
    )
    return dict(categories=categories_with_counts)

@app.route('/category/<slug>')
def category_view(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    products = category.products.all()  # Assuming lazy='dynamic'
    return render_template('category.html', category=category, products=products)


@app.route('/category/list', endpoint='category_list_app')
def category_list():
    categories = Category.query.all()
    return render_template('product_category_list.html', categories=categories)

@app.route('/category/add', methods=['GET', 'POST'], endpoint='category_list_admin')
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('category_list'))
    return render_template('product_add_category.html')

# Tag Routes
@app.route('/tag/list')
def tag_list():
    tags = Tag.query.all()
    return render_template('tag_list.html', tags=tags)

@app.route('/tag/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        name = request.form['name']
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for('tag_list'))
    return render_template('add_tag.html')

# Product Routes
@app.route('/product/list')
def product_list():
    products = Product.query.all()
    return render_template('product_list.html', products=products)

@app.route('/product/add', methods=['GET', 'POST'])
def add_product():
    categories = Category.query.all()
    tags = Tag.query.all()

    upload_folder = 'static/uploads/products'
    gallery_folder = 'static/uploads/products/gallery'
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(gallery_folder, exist_ok=True)

    if request.method == 'POST':
        name = request.form['name']
        regular_price = float(request.form['regular_price'])
        sale_price = request.form.get('sale_price')
        sale_price = float(sale_price) if sale_price else None
        short_description = request.form.get('short_description')
        description = request.form.get('description')
        meta_title = request.form.get('meta_title')
        meta_description = request.form.get('meta_description')
        twitter_title = request.form.get('twitter_title')
        twitter_description = request.form.get('twitter_description')
        og_title = request.form.get('og_title')
        og_description = request.form.get('og_description')

        category_id = int(request.form['category'])
        selected_tags = request.form.getlist('tags')

        product = Product(
            name=name,
            slug=slugify(name),
            regular_price=regular_price,
            sale_price=sale_price,
            short_description=short_description,
            description=description,
            meta_title=meta_title,
            meta_description=meta_description,
            twitter_title=twitter_title,
            twitter_description=twitter_description,
            og_title=og_title,
            og_description=og_description,
            category_id=category_id,
        )

        for tag_id in selected_tags:
            tag = Tag.query.get(int(tag_id))
            if tag:
                product.tags.append(tag)

        # Handle main product image upload
        main_image = request.files.get('product_image')
        if main_image and main_image.filename:
            filename = secure_filename(main_image.filename)
            filepath = os.path.join(upload_folder, filename)
            main_image.save(filepath)
            product.product_image = '/' + filepath  # store relative URL/path

        db.session.add(product)
        db.session.commit()

        # Handle gallery images upload after committing product to get its ID
        gallery_files = request.files.getlist('gallery_images')
        for file in gallery_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                gallery_path = os.path.join(gallery_folder, filename)
                file.save(gallery_path)
                gallery_image = ProductGallery(image_url='/' + gallery_path, product=product)
                db.session.add(gallery_image)

        db.session.commit()

        flash('Product added successfully', 'success')
        return redirect(url_for('product_list'))
    
    return render_template('add_product.html', categories=categories, tags=tags)




@app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'], endpoint='edit_product')
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    tags = Tag.query.all()

    upload_folder = 'static/uploads/products'
    gallery_folder = 'static/uploads/products/gallery'
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(gallery_folder, exist_ok=True)

    if request.method == 'POST':
        product.name = request.form['name']
        slug = request.form.get('slug').strip()
        product.slug = slugify(slug) if slug else slugify(product.name)
        product.regular_price = float(request.form['regular_price'])
        sale_price = request.form.get('sale_price')
        product.sale_price = float(sale_price) if sale_price else None
        product.short_description = request.form.get('short_description')
        product.description = request.form.get('description')
        product.category_id = int(request.form['category'])

        selected_tag_ids = request.form.getlist('tags')
        product.tags = []
        for tag_id in selected_tag_ids:
            tag = Tag.query.get(int(tag_id))
            if tag:
                product.tags.append(tag)

        main_image = request.files.get('product_image')
        if main_image and main_image.filename:
            filename = secure_filename(main_image.filename)
            image_path = os.path.join('static/uploads/products', filename)
            main_image.save(image_path)
            product.product_image = '/' + image_path

        gallery_files = request.files.getlist('gallery_images')
        for file in gallery_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                gallery_path = os.path.join('static/uploads/products/gallery', filename)
                file.save(gallery_path)
                gallery_image = ProductGallery(image_url='/' + gallery_path, product=product)
                db.session.add(gallery_image)

        schema_json = request.form.get('schema_json')
        if schema_json:
            schema_obj = product.schemas.first()
            if schema_obj:
                schema_obj.schema_json = schema_json
            else:
                new_schema = ProductSchema(schema_json=schema_json, product=product)
                db.session.add(new_schema)

        product.meta_title = request.form.get('meta_title')
        product.meta_description = request.form.get('meta_description')
        product.twitter_title = request.form.get('twitter_title')
        product.twitter_description = request.form.get('twitter_description')
        product.og_title = request.form.get('og_title')
        product.og_description = request.form.get('og_description')

        try:
            db.session.commit()
            flash('Product updated successfully.', 'success')
            return redirect(url_for('product_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {e}', 'danger')

    return render_template('edit_product.html', product=product, categories=categories, tags=tags)


@app.route('/products')
def product_display():
    products = Product.query.all()
    return render_template('frontend/product_display.html', products=products)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    product = Product.query.get(product_id)
    if not product:
        flash('Invalid product.', 'danger')
        return redirect(url_for('product_display'))

    # Simple cart implementation in session
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    session['cart'] = cart
    flash(f'Added {product.name} to cart.', 'success')
    return redirect(url_for('product_display'))

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This creates the Banner table if not exists
    app.run(debug=True)
    # app.run(port=5001, debug=True)

