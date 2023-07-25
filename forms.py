from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms import BooleanField, IntegerField, DateField, ValidationError
from wtforms.validators import DataRequired, Length, Email
from wtforms.validators import EqualTo, NumberRange
from wtforms.fields import DateField
from datetime import date


# list of valid countries to be searched from using search api
# the two letter codes are needed to call the api
valid_countries = {
    'ar' : 'ae',
    'de': 'de',
    'en': 'us',
    'es': 'mx',
    'fr': 'fr',
    'he': 'il',
    'it': 'it',
    'nl': 'nl',
    'no': 'no',
    'pt': 'pt',
    'ru': 'ru',
    'sv': 'se',
    'uk': 'ua',
    'da': 'dk',
    'zh': 'hk'
}


valid_languages = {
    'Arabic': 'ar',
    'German': 'de',
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'Hebrew': 'he',
    'Italian': 'it',
    'Dutch': 'nl',
    'Norwegian': 'no',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Swedish': 'sv',
    'Ukrainian': 'uk',
    'Danish': 'da',
    'Chinese': 'zh'
}



class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=5, max=20), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SearchForm(FlaskForm):

    # checks if the inputed country is one of the supported countries
    def validate_nation(form, field):
        if field.data not in valid_countries:
            raise ValidationError("Invalid country, or country is not supported")
    
    # checks if the inputed language is one of the supported languages
    def validate_language(form, field):
        if field.data not in valid_languages:
            raise ValidationError("Invalid language, or language is not supported")

    # define form inputs
    search_input = StringField(validators=[DataRequired(), Length(min=1)])
    date = DateField('Starting From', format = '%Y-%m-%d', default = date.today())
    nation = StringField('Country', default = 'United States', validators=[validate_nation, Length(min=1, max=50)])
    language = StringField('Language', default = 'United States', validators=[validate_language, Length(min=1, max=50)])
    update_interval = IntegerField('Update every __ day(s)', validators=[NumberRange(min=1, max=31)])
    source = StringField('News Source', validators=[Length(min=1, max=50)])
    submit = SubmitField('Search')