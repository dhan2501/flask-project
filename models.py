# models.py
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(512), nullable=False)
    nickname = db.Column(db.String(50), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)  # Avatar image URL or path

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)        # URL or path to banner image
    alt_text = db.Column(db.String(150), nullable=True)          # Alt text for accessibility
    read_more_link = db.Column(db.String(255), nullable=True)    # URL for read more button
    heading = db.Column(db.String(200), nullable=False)          # Main heading text
    sub_heading = db.Column(db.String(300), nullable=True)       # Subheading or description

    def __repr__(self):
        return f"<Banner {self.heading}>"

class BlogCategory(db.Model):
    __tablename__ = 'blog_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<BlogCategory {self.name}>"    

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id'))
    category = db.relationship('BlogCategory', backref='blogs')
    
    # Blog content fields
    image_url = db.Column(db.String(255), nullable=False)       # URL or path to blog image
    alt_text = db.Column(db.String(150), nullable=True)         # Alt text for image accessibility
    short_description = db.Column(db.String(500), nullable=True) # Short summary or excerpt
    description = db.Column(db.Text, nullable=False)             # Full blog content
    
    # SEO related fields
    meta_title = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.String(500), nullable=True)
    meta_keywords = db.Column(db.String(255), nullable=True)      # Comma separated keywords

     # Social Media related fields
    twitter_title = db.Column(db.String(255), nullable=True)
    twitter_description = db.Column(db.String(500), nullable=True)
    twitter_keywords = db.Column(db.String(255), nullable=True)      # Comma separated keywords
    
    # Additional schema fields - example: JSON for extensibility
    schema_data = db.Column(db.JSON, nullable=True)              # To store multiple schema data in JSON
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __repr__(self):
        return f"<Blog {self.meta_title or self.short_description[:30]}>"




# Association table for Product <-> Tag many-to-many relationship
product_tags = db.Table('product_tags',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    meta_image = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=False)
    products = db.relationship('Product', back_populates='category', lazy='dynamic')

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.slug = slugify(name)  # auto-generate slug

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', secondary=product_tags, back_populates='tags', lazy='dynamic')

class ProductGallery(db.Model):
    __tablename__ = 'product_gallery'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

class ProductSchema(db.Model):
    __tablename__ = 'product_schema'
    id = db.Column(db.Integer, primary_key=True)
    schema_json = db.Column(db.Text)  # stores rich snippet/schema markup
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    regular_price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=True)
    short_description = db.Column(db.String(255))
    description = db.Column(db.Text)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    meta_image = db.Column(db.String(255))
    twitter_title = db.Column(db.String(255))
    twitter_description = db.Column(db.Text)
    og_title = db.Column(db.String(255))
    og_description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='products')
    tags = db.relationship('Tag', secondary=product_tags, back_populates='products', lazy='dynamic')
    product_image = db.Column(db.String(255))  # main product image path or URL
    gallery_images = db.relationship('ProductGallery', backref='product', lazy='dynamic')
    schemas = db.relationship('ProductSchema', backref='product', lazy='dynamic')

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.slug = slugify(name)  # auto-generate slug

