from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Optional,Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number')
    nickname = StringField('Nickname')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    nickname = StringField('Nickname', validators=[Optional()])
    avatar = FileField('Avatar Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    password = PasswordField('New Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Update Profile')


# class SettingsForm(FlaskForm):
#     new_password = PasswordField('New Password', validators=[Optional()])
#     confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('new_password', message='Passwords must match')])
#     email_notifications = BooleanField('Email Notifications')
#     submit = SubmitField('Save Settings')

class SettingsForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired(message='Please enter your old password.')])
    new_password = PasswordField('New Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('new_password', message='Passwords must match')])
    email_notifications = BooleanField('Email Notifications')
    submit = SubmitField('Save Settings')


class BannerForm(FlaskForm):
    image = FileField('Banner Image', validators=[
        Optional(),  # <-- Change from FileRequired() to Optional()
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    alt_text = StringField('Alt Text', validators=[Optional()])
    read_more_link = StringField('Read More Link', validators=[Optional()])
    heading = StringField('Heading', validators=[DataRequired()])
    sub_heading = StringField('Sub Heading', validators=[Optional()])
    submit = SubmitField('Update Banner')


class BlogForm(FlaskForm):
    image = FileField('Blog Image', validators=[Optional()])
    alt_text = StringField('Alt Text', validators=[Optional()])
    short_description = StringField('Short Description', validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    
    meta_title = StringField('Meta Title', validators=[Optional()])
    meta_description = TextAreaField('Meta Description', validators=[Optional()])
    meta_keywords = StringField('Meta Keywords', validators=[Optional()])
    
    twitter_title = StringField('Twitter Title', validators=[Optional()])
    twitter_description = TextAreaField('Twitter Description', validators=[Optional()])
    twitter_keywords = StringField('Twitter Keywords', validators=[Optional()])
    
    # You can add a field or JSON input for schema_data or handle it separately
    
    submit = SubmitField('Submit')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save')