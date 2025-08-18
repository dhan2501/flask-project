# models.py
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(512), nullable=False)
    nickname = db.Column(db.String(50), nullable=True)

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