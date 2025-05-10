from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FileField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from flask_wtf.file import FileAllowed
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class MealPlanForm(FlaskForm):
    diet_type = SelectField('Preferred Diet', 
                           choices=[('Anything', 'Anything'), 
                                   ('Keto', 'Keto'), 
                                   ('Mediterranean', 'Mediterranean'), 
                                   ('Paleo', 'Paleo'), 
                                   ('Vegan', 'Vegan'), 
                                   ('Vegetarian', 'Vegetarian')])
    target_calories = IntegerField('Daily Calorie Target', validators=[DataRequired(), NumberRange(min=800, max=5000)])
    meal_count = SelectField('Number of Meals per Day', 
                            choices=[(3, '3 meals'), (4, '4 meals'), (5, '5 meals'), (6, '6 meals')],
                            coerce=int)
    submit = SubmitField('Generate Meal Plan')

class UploadDietaryDataForm(FlaskForm):
    date = StringField('Date (YYYY-MM-DD)', validators=[DataRequired()])
    calories = IntegerField('Total Calories', validators=[DataRequired(), NumberRange(min=0)])
    protein = IntegerField('Protein (g)', validators=[DataRequired(), NumberRange(min=0)])
    carbs = IntegerField('Carbohydrates (g)', validators=[DataRequired(), NumberRange(min=0)])
    fat = IntegerField('Fat (g)', validators=[DataRequired(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])
    meals_json = HiddenField('Meals Data')
    submit = SubmitField('Save Data')

class UploadCSVForm(FlaskForm):
    csv_file = FileField('Upload CSV', validators=[
        DataRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Upload File')
class ShareDataForm(FlaskForm):
    recipient_username = StringField('Username to share with', validators=[DataRequired()])
    data_type = SelectField('Data Type', choices=[('meal_plan', 'Meal Plan'), ('dietary_data', 'Dietary Data')])
    data_id = IntegerField('Data ID', validators=[DataRequired()])
    submit = SubmitField('Share')
    
    def validate_recipient_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('User not found. Please check the username.')
