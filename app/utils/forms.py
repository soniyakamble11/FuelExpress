from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField, FloatField, DateField, TimeField, TextAreaField, RadioField,IntegerField, DecimalField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Account Type', choices=[
        ('customer', 'Customer'),
        ('station_owner', 'Fuel Station Owner'),
        ('delivery_partner', 'Delivery Partner')
    ], default='customer')
    submit = SubmitField('Create Account')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Use a different email.')
    
    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('Phone number already registered.')


class AddressForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    address_line1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line2 = StringField('Address Line 2')
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    pincode = StringField('Pincode', validators=[DataRequired()])
    is_default = BooleanField('Set as Default Address')
    submit = SubmitField('Save Address')

class OrderFuelForm(FlaskForm):
    fuel_id = RadioField('Fuel', choices=[], validators=[DataRequired()])
    quantity = DecimalField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    address_id = RadioField('Address', choices=[], validators=[DataRequired()])
    delivery_date = DateField('Delivery Date', validators=[DataRequired()])
    delivery_time = TimeField('Delivery Time', validators=[DataRequired()])
    special_instructions = TextAreaField('Special Instructions')
    submit = SubmitField('Place Order')

class PaymentForm(FlaskForm):
    payment_mode = RadioField(
        'Payment Mode',
        choices=[('COD','Cash on Delivery'), ('Online','Online Payment')],
        default='COD'
    )
    submit = SubmitField('Pay Now')