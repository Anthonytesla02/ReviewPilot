from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField, DateTimeField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, URL
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=200)])
    google_business_url = StringField('Google Business Profile URL', validators=[Optional(), URL()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ReviewTemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(min=2, max=200)])
    subject = StringField('Email Subject', validators=[DataRequired(), Length(min=5, max=300)])
    message = TextAreaField('Email Message', validators=[DataRequired(), Length(min=10)], 
                           widget=TextArea(), render_kw={"rows": 8})
    is_default = BooleanField('Set as Default Template')
    submit = SubmitField('Save Template')

class CustomerForm(FlaskForm):
    name = StringField('Customer Name', validators=[DataRequired(), Length(min=2, max=200)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    appointment_date = DateTimeField('Appointment Date', validators=[Optional()], format='%Y-%m-%d %H:%M')
    service_type = StringField('Service Type', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Notes', validators=[Optional()], render_kw={"rows": 3})
    submit = SubmitField('Save Customer')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], 
                        coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Your Review', validators=[Optional()], render_kw={"rows": 5})
    submit = SubmitField('Submit Review')

class AdminResponseForm(FlaskForm):
    admin_response = TextAreaField('Your Response', validators=[DataRequired()], render_kw={"rows": 5})
    submit = SubmitField('Send Response')

class SettingsForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=200)])
    google_business_url = StringField('Google Business Profile URL', validators=[Optional(), URL()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Settings')

class SendReviewRequestForm(FlaskForm):
    customer_id = HiddenField('Customer ID', validators=[DataRequired()])
    template_id = SelectField('Review Template', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Send Review Request')
