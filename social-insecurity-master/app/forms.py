from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField, validators
from wtforms.fields.html5 import DateField

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.Required()],render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', validators=[validators.Required()], render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):

    username_validator = [
        validators.Regexp(
            "^[A-Za-z_][A-Za-z0-9_]{1,29}$", # 1(non number) + (1-4) alphanumeric or underscore
            message="Username must be 2-30 characters long, not start with a number, and can only contain letters, numbers, and underscores"),
    ]
    firstname_validator = [
        validators.Regexp(
            "^[A-Za-z]{1,30}$", # contains 1-30 letters
            message="First Name must be 1-30 characters long, and can only contain letters"),
    ]
    lastname_validator = [
        validators.Regexp(
            "^[A-Za-z]{1,30}$", # contains 1-30 letters
            message="Last Name must be 1-30 characters long, and can only contain letters"),
    ]
    password_validator = [
        validators.Regexp( # contains 8-128 characters, 1 uppercase, 1 lowercase, 1 number
            "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,128}$",
            message="Password must be 8-128 characters long, at least one uppercase letter, one lowercase letter and one number"),
    ]
    confirm_password_validator = [
        validators.EqualTo( # must match password field
            'password', 
            message='Passwords must match')
    ]
    first_name = StringField('First Name', validators=firstname_validator, render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name', validators=lastname_validator, render_kw={'placeholder': 'Last Name'})
    username = StringField('Username', validators=username_validator, render_kw={'placeholder': 'Username'},)
    password = PasswordField('Password', validators=password_validator, render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', confirm_password_validator, render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image')
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    education = StringField('Education', render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
