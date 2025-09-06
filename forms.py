from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class UpdateAccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    verification_code = StringField('Verification Code')  # اختياري حسب حالتك
    old_password = PasswordField('Old Password')
    new_password = PasswordField('New Password', validators=[Length(min=9)])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('new_password', message="Passwords must match")])
    submit = SubmitField('Update')


