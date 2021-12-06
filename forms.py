from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Length, DataRequired, EqualTo


# form for registration
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=10)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    valid_word = PasswordField('Confirm Password',
                               validators=[DataRequired(), Length(min=8), EqualTo('Password')])
    submit = SubmitField('Register')


# form for login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=10)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
