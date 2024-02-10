from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, RadioField, SelectField, SelectMultipleField, StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, NumberRange
from application.models import User
from flask_wtf.file import FileField, FileAllowed


class RegisterForm(FlaskForm):
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')

    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class ReviewForm(FlaskForm):
    review = StringField(label='Review Text', validators=[DataRequired()])
    submit = SubmitField(label='Submit Review')

class AddBookForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    price = StringField(label='Price', validators=[DataRequired()])
    barcode = StringField(label='Barcode', validators=[DataRequired(), Length(min=12, max=12, message="Barcode must be 12 characters long")])
    genre = SelectField(label='Genre', choices=[('fiction', 'Fiction'), ('non-fiction', 'Non-Fiction'), ('mystery', 'Mystery'), ('science-fiction', 'Science Fiction'), ('fantasy', 'Fantasy'), ('romance', 'Romance'), ('thriller', 'Thriller'), ('biography', 'Biography'), ('history', 'History'), ('self-help', 'Self-Help')], validators=[DataRequired()])
    description2 = StringField(label='Description', validators=[DataRequired()])
    author = StringField(label='Author', validators=[DataRequired()])
    releaseYear = StringField(label='Release Year', validators=[DataRequired(), Length(min=4, max=4, message="Release year must be 4 characters long")])
    blurb = StringField(label='Blurb', validators=[DataRequired()])
    stock = StringField(label='Stock', validators=[DataRequired()])
    book_picture = FileField(label='Book Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField(label='Add Book')

class EditBookForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    price = StringField(label='Price', validators=[DataRequired()])
    barcode = StringField(label='Barcode', validators=[DataRequired(), Length(min=12, max=12, message="Barcode must be 12 characters long")])
    genre = SelectField(label='Genre', choices=[('fiction', 'Fiction'), ('non-fiction', 'Non-Fiction'), ('mystery', 'Mystery'), ('science-fiction', 'Science Fiction'), ('fantasy', 'Fantasy'), ('romance', 'Romance'), ('thriller', 'Thriller'), ('biography', 'Biography'), ('history', 'History'), ('self-help', 'Self-Help')], validators=[DataRequired()])
    description2 = StringField(label='Description', validators=[DataRequired()])
    author = StringField(label='Author', validators=[DataRequired()])
    releaseYear = StringField(label='Release Year', validators=[DataRequired(), Length(min=4, max=4, message="Release year must be 4 characters long")])
    blurb = StringField(label='Blurb', validators=[DataRequired()])
    stock = StringField(label='Stock', validators=[DataRequired()])
    submit = SubmitField(label='Save Changes')

class AddToBasketForm(FlaskForm):
    quantity = IntegerField('Quantity:', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add to Basket')

class BookFilterForm(FlaskForm):
    genres = SelectMultipleField('Genres', choices=[
        ('fiction', 'Fiction'), ('non-fiction', 'Non-Fiction'), ('mystery', 'Mystery'), ('science-fiction', 'Science Fiction'), ('fantasy', 'Fantasy'), ('romance', 'Romance'), ('classic', 'Classic'), ('thriller', 'Thriller'), ('biography', 'Biography'), ('history', 'History'), ('self-help', 'Self-Help')
        # Add more genres as needed
    ], coerce=str)

    submit = SubmitField('Apply Filters')

class GenreForm(FlaskForm):
    fiction = BooleanField('Fiction')
    non_fiction = BooleanField('Non-Fiction')
    mystery = BooleanField('Mystery')
    science_fiction = BooleanField('Science Fiction')
    fantasy = BooleanField('Fantasy')
    romance = BooleanField('Romance')
    classic = BooleanField('Classic')
    thriller = BooleanField('Thriller')
    biography = BooleanField('Biography')
    history = BooleanField('History')
    self_help = BooleanField('Self-Help')

    under5 = BooleanField('Under £5')
    filter5_10 = BooleanField('£5-£10')
    filter10_15 = BooleanField('£10-£15')
    filter15_20 = BooleanField('£15-£20')
    filter20_25 = BooleanField('£20-£25')

    # Sorting options as radio buttons
    sorting = RadioField('Sort by', choices=[
        ('recommended', 'Recommended'),
        ('alphabetical', 'Alphabetical (A-Z)'),
        ('price_low_high', 'Price Low to High'),
        ('price_high_low', 'Price High to Low')
    ], default='recommended')

    submit = SubmitField('Apply Filters')
