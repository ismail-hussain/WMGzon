# File where you will setup the test environment as well as anything that needs to be created before any tests
import pytest

from application import create_app, db, add_fake_books, add_fake_reviews, add_fake_users, add_fake_sales
from application.models import User, Book, Review, Sale
from flask_login import login_user, logout_user
#Fixtures

@pytest.fixture
def client():
    env = "TEST"
    # Initialise test app
    app = create_app(env)

    # Create a test client to which we can make requests
    client = app.test_client()

    # Create a test database with some test data
    with app.app_context():
        
        # Drop all tables (erase all data)
        db.drop_all()

        # Create all tables based on the models
        db.create_all()

        # Add fake data
        add_fake_users()
        add_fake_books()
        add_fake_reviews()
        add_fake_sales()

        
        db.session.commit()
    
    return client

# Fixture for simulating user login.
# This fixture sets up a test user session by logging in as a predefined user.
# It uses the Flask test request context to create a simulated client session.
# Once the test user session is set up, the client is yielded to the test function.
# After the test function finishes execution, it logs out the user to clean up the session.
@pytest.fixture
def login_as_user(client):
    with client.application.test_request_context():  # Creates a request context
        user_email = "user1@example.com"
        test_user = User.query.filter_by(email_address=user_email).first()
        if test_user:
            login_user(test_user)
        yield client
        logout_user()

# Fixture for simulating admin login.
# This fixture sets up a test admin session by logging in as a predefined admin user.
# It fetches the admin user by email address and logs them in using Flask-Login.
# It then yields the client to the test function.
# After the test function finishes execution, it logs out the admin user to clean up the session.
@pytest.fixture
def login_as_admin(client):
    # Fetch the user by email
    user_email = 'user3@example.com'
    test_user = User.query.filter_by(email_address=user_email).first()
    # Log in the user
    print(test_user.id)
    with client.application.test_request_context():
        login_user(test_user)
        yield client
    logout_user()

# Fixture for adding a book with an image.
# This fixture is used to test the loading of an image associated with a book.
# It prepares example binary data for an image and retrieves a book from the database.
# It then returns the ID of the retrieved book, which can be used in tests to check if the image loads correctly.
@pytest.fixture
def add_book_with_image():
    book_picture_data = b'\x89PNG\r\n\x1a\n...'  # Example binary data for an image
    new_book = Book.query.filter_by(id=1).first()
    
    return new_book.id
