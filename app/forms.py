from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FileField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from flask_wtf.file import FileAllowed
from models import User


class ShareDataForm(FlaskForm):
    recipient_username = StringField('Username to share with', validators=[DataRequired()])
    data_type = SelectField('Data Type', choices=[('meal_plan', 'Meal Plan'), ('dietary_data', 'Dietary Data')])
    data_id = IntegerField('Data ID', validators=[DataRequired()])
    submit = SubmitField('Share')
    
    def validate_recipient_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('User not found. Please check the username.')