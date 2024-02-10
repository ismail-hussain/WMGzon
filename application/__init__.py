# Create the server
# Add a listener
from datetime import datetime, timedelta
from random import randint, randrange
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# Run the server
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')



#Define DB
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


# Application factory
def create_app(env=None):
    # Initialisation of the app
    app = Flask(__name__)

    # Set up the environment variables depending on the environment
    if env == 'TEST':
        app.config['TESTING']=True
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['SERVER_NAME'] = 'localhost.localdomain'
        app.config['SECRET_KEY'] = 'bd85be78920be1be8d1c6f4a'
    else:
        app.config['TESTING']=False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///market.db"
        app.config['SECRET_KEY'] = 'bd85be78920be1be8d1c6f4a'

    # Connection of the DB to the app
    db.init_app(app)
    # Makes sure DB is created in an application context
    app.app_context().push()

    CORS(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login_page"
    login_manager.login_message_category = "info"

    from application.routes import main, users, books, reviews
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(books)
    app.register_blueprint(reviews)


    return app

from application.models import User, Book, Review, Sale
def add_fake_users():
    fake_users = [
        User(email_address=f'user{i}@example.com', password_hash=f'$2b$12$ztfPkK9dcG4GvHc2g2eIG.udi/H1GI/HGxg0Cl76r2Da2lX9T1.M2', is_admin=(i % 3 == 0))
        for i in range(1, 11)
    ]

    db.session.add_all(fake_users)
    db.session.commit()

def add_fake_books():
    fake_books = [
        Book(title='To Kill a Mockingbird', price=15, barcode='123456789012', description='A classic novel', 
             author='Harper Lee', release_year=1960, genre='fiction', blurb='Compelling story of racial injustice', stock=100, book_picture= open(os.path.join(STATIC_FOLDER, 'assets', 'to-kill-a-mockingbird-front.jpg'), 'rb').read()),
        Book(title='1984', price=21, barcode='987654321098', description='Dystopian novel', 
             author='George Orwell', release_year=1949, genre='science-fiction', blurb='A warning against totalitarianism', stock=60, book_picture= open(os.path.join(STATIC_FOLDER, 'assets', '1984-front.jpg'), 'rb').read()),
        Book(title='The Great Gatsby', price=13, barcode='234567890123', description='Roaring Twenties tale', 
             author='F. Scott Fitzgerald', release_year=1925, genre='classic', blurb='Glamour, love, and tragedy', stock=0, book_picture= open(os.path.join(STATIC_FOLDER, 'assets', 'the-great-gatsby-front.jpg'), 'rb').read()),
        Book(title='Harry Potter ', price=3, barcode='345678901234', 
             description='Magical adventure', author='J.K. Rowling', release_year=1997, genre='fantasy', 
             blurb='The start of the beloved Harry Potter series', stock=25, book_picture= open(os.path.join(STATIC_FOLDER, 'assets', 'harry-potter-and-the-sorcerers-stone-chapter6.jpg'), 'rb').read()),
        Book(title='Pride and Prejudice', price=22, barcode='456789012345', description='Romantic novel', 
             author='Jane Austen', release_year=1813, genre='classic', blurb='A tale of love and societal expectations', stock=0, book_picture= open(os.path.join(STATIC_FOLDER, 'assets', 'pride-and-prejudice-front.jpg'), 'rb').read()),
        Book(title='The Hobbit', price=12, barcode='567890123456', description='Fantasy adventure', 
             author='J.R.R. Tolkien', release_year=1937, genre='fantasy', blurb='Bilbo Baggins\' journey', stock=3, book_picture= open(os.path.join(STATIC_FOLDER, 'assets', 'the-hobbit-front.jpg'), 'rb').read()),
        Book(title='The Catcher in the Rye', price=9, barcode='678901234567', description='Coming-of-age novel', 
             author='J.D. Salinger', release_year=1951, genre='fiction', blurb='Holden Caulfield\'s story', stock=21, book_picture= open(os.path.join(STATIC_FOLDER, 'assets', 'the-catch-in-the-rye-front.jpg'), 'rb').read()),
        Book(title='Brave New World', price=18, barcode='789012345678', description='Dystopian novel', 
             author='Aldous Huxley', release_year=1932, genre='science-fiction', blurb='A world of genetic engineering', stock=1,book_picture= open(os.path.join(STATIC_FOLDER, 'assets', 'brave-new-world-front.jpg'), 'rb').read()),
        Book(title='The Lord of the Rings', price=25, barcode='890123456789', description='Epic fantasy trilogy', 
             author='J.R.R. Tolkien', release_year=1954, genre='fantasy', blurb='Frodo\'s quest to destroy the One Ring', stock=9, book_picture= open(os.path.join(STATIC_FOLDER, 'assets', 'the-lord-of-the-rings-front.jpg'), 'rb').read()),
        Book(title='Moby-Dick', price=22, barcode='901234567890', description='Whaling adventure', 
             author='Herman Melville', release_year=1851, genre='adventure', blurb='Captain Ahab and the white whale', stock=42, book_picture= open(os.path.join(STATIC_FOLDER, 'assets', 'moby-dick-front.jpg'), 'rb').read()),
        # Add more books as needed
    ]

    db.session.add_all(fake_books)
    db.session.commit()


def add_fake_reviews():
    # Define current time once to avoid slight discrepancies
    current_time = datetime.now()
    fake_reviews = [
        Review(book_id=1, user_id=1, review_text='A timeless classic!', rating=3, date=current_time - timedelta(days=5)),
        Review(book_id=2, user_id=2, review_text='Dystopian masterpiece.', rating=4, date=current_time - timedelta(days=4)),
        Review(book_id=3, user_id=3, review_text='Captivating story!', rating=5, date=current_time - timedelta(days=14)),
        Review(book_id=4, user_id=4, review_text='Magical and enchanting.', rating=5,date=current_time - timedelta(days=13)),
        Review(book_id=5, user_id=5, review_text='Beautiful love story.', rating=5,date=current_time - timedelta(days=10)),
        Review(book_id=6, user_id=6, review_text='An epic adventure!', rating=3,date=current_time - timedelta(days=6)),
        Review(book_id=7, user_id=7, review_text='Relatable coming-of-age tale.', rating=3,date=current_time - timedelta(days=8)),
        Review(book_id=8, user_id=8, review_text='Thought-provoking dystopia.', rating=4,date=current_time - timedelta(days=3)),
        Review(book_id=9, user_id=9, review_text='Epic fantasy trilogy!', rating=5,date=current_time - timedelta(days=2)),
        Review(book_id=10, user_id=10, review_text='A thrilling adventure.', rating=3,date=current_time - timedelta(days=1)),
        # Add more reviews as needed
    ]

    db.session.add_all(fake_reviews)
    db.session.commit()

def add_fake_sales():
    # Define current time once to avoid slight discrepancies
    current_time = datetime.now()
    fake_sales = [
        # Sales from earlier in the past year
        Sale(book_id=1, quantity_sold=230, sale_date=current_time - timedelta(days=330)),
        Sale(book_id=2, quantity_sold=210, sale_date=current_time - timedelta(days=300)),
        Sale(book_id=3, quantity_sold=162, sale_date=current_time - timedelta(days=270)),
        Sale(book_id=4, quantity_sold=1600, sale_date=current_time - timedelta(days=240)),
        Sale(book_id=5, quantity_sold=320, sale_date=current_time - timedelta(days=210)),
        Sale(book_id=6, quantity_sold=320, sale_date=current_time - timedelta(days=180)),
        Sale(book_id=7, quantity_sold=276, sale_date=current_time - timedelta(days=150)),
        Sale(book_id=8, quantity_sold=122, sale_date=current_time - timedelta(days=120)),
        Sale(book_id=9, quantity_sold=181, sale_date=current_time - timedelta(days=90)),
        Sale(book_id=10, quantity_sold=147, sale_date=current_time - timedelta(days=60)),
        Sale(book_id=1, quantity_sold=34, sale_date=current_time - timedelta(days=30)),
        Sale(book_id=2, quantity_sold=58, sale_date=current_time - timedelta(days=28)),
        Sale(book_id=3, quantity_sold=29, sale_date=current_time - timedelta(days=26)),
        Sale(book_id=4, quantity_sold=49, sale_date=current_time - timedelta(days=24)),
        Sale(book_id=5, quantity_sold=60, sale_date=current_time - timedelta(days=22)),
        Sale(book_id=6, quantity_sold=56, sale_date=current_time - timedelta(days=20)),
        
        
        # Sales from the current month
        Sale(book_id=5, quantity_sold=43, sale_date=current_time - timedelta(days=2)),
        Sale(book_id=6, quantity_sold=63, sale_date=current_time - timedelta(days=2)),
        Sale(book_id=7, quantity_sold=52, sale_date=current_time - timedelta(days=1)),
        Sale(book_id=8, quantity_sold=32, sale_date=current_time - timedelta(days=1)),
        Sale(book_id=9, quantity_sold=78, sale_date=current_time),
        Sale(book_id=10, quantity_sold=69, sale_date=current_time),
    ]
    db.session.add_all(fake_sales)
    db.session.commit()
