import pytest
from flask import url_for
from application.models import User
from flask_login import login_user

def test_books_page_get(client):
    
    response = client.get(url_for('books.book_page'))
    assert response.status_code == 200
    # Check if the response contains titles from the fake data
    assert b'To Kill a Mockingbird' in response.data
    assert b'1984' in response.data
    

def test_books_page_post(client):
    
    # Example: Filtering by 'fiction' genre
    response = client.post(url_for('books.book_page'), data={
        'fiction': True,
        # Include other form fields as necessary
    }, follow_redirects=True)

    assert response.status_code == 200
    # Check that the response includes books from the 'fiction' genre
    assert b'To Kill a Mockingbird' in response.data
    assert b'The Catcher in the Rye' in response.data
    
def test_book_page_get(client):
    # Use the correct URL for the book's detail page, assuming ID 1 for simplicity
    response = client.get('/books/1')
    assert response.status_code == 200
    # Check if the response contains specific content expected to be rendered by the template
    assert b"To Kill a Mockingbird" in response.data  # Assuming the book "1984" is in the database with ID 1
    # Optionally, check for other specific content like author name, book description, etc.

def test_search_books_by_title_post(client):
    
    test_title = "To Kill a Mockingbird"  
    response = client.post('/search', data={'search': test_title}, follow_redirects=True)
    assert response.status_code == 200
    assert b"To Kill a Mockingbird" in response.data
    assert bytes(test_title, 'utf-8') in response.data  # Check that the search result is in the response

def test_search_books_by_author_post(client):
    
    test_author = "J.R.R. Tolkien"  
    response = client.post('/search', data={'search': test_author}, follow_redirects=True)
    assert response.status_code == 200
    assert b"The Hobbit" in response.data
    assert b"The Lord of the Rings" in response.data
    assert bytes(test_author, 'utf-8') in response.data 

def test_unsuccessful_login(client):
    
    invalid_credentials = {
        'email_address': 'wrong@example.com',
        'password': 'wrongpassword',
    }
    response = client.post('/login', data=invalid_credentials, follow_redirects=True)
    assert response.status_code == 200
    print(response.data)
    assert b'Login Page' in response.data
    
def test_successful_login(client):
    
    valid_credentials = {
        'email_address': 'user1@example.com',
        'password': 'password',
    }
    response = client.post('/login', data=valid_credentials, follow_redirects=True)
    assert response.status_code == 200
    assert b'user1@example.com' in response.data
    # Further checks can include verifying the redirection to the main page or checking for the user's presence in the session

def test_basket_page_unauthenticated(client):
    response = client.get('/basket', follow_redirects=True)
    assert b'Please log in to view your basket.' in response.data
    assert b'Login' in response.data

def test_basket_page_authenticated(login_as_user, client):
    # login_as_user is a fixture that logs in a user
    response = client.get('/basket')
    assert response.status_code == 200
    
    assert b'Basket' in response.data

def test_wishlist_page_unauthenticated(client):
    response = client.get('/wishlist', follow_redirects=True)
    assert b'Please log in to view your wishlist.' in response.data
    assert b'Login' in response.data  # Assuming the login page has 'Login' in its content

def test_wishlist_page_authenticated(login_as_user, client):
    response = client.get('/wishlist')
    assert response.status_code == 200
    print(response.data)
    assert b'items in wishlist' in response.data  # Check for a unique element present in the wishlist page


    
def test_display_with_valid_book_id(client, add_book_with_image):
    book_id = add_book_with_image  # Get the ID from the fixture
    response = client.get(f'/display/{book_id}')
    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'
    # Optionally, check some portion of the image data if known
    assert response.data[:4] == b'\xff\xd8\xff\xe0'  # JPEG file signature

def test_main_page_authenticated_regular_user(client):
    response = client.get('/main')
    assert response.status_code == 200
    # Check if the 'admin' variable is correctly recognized as False
    # This assumes your template renders this condition in some detectable way
    print(response.data)
    assert b'Main Page' in response.data
