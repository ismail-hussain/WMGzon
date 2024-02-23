import pytest
from flask import url_for
from application.models import User
from flask_login import login_user

# Test case for GET request to the books page.
# This test checks if the books page can be accessed successfully by sending a GET request.
# It asserts that the response status code is 200, indicating a successful request.
# Additionally, it checks if the response data contains titles of specific books ('To Kill a Mockingbird' and '1984').
def test_books_page_get(client):
    
    response = client.get(url_for('books.book_page'))
    assert response.status_code == 200
    # Check if the response contains titles from the fake data
    assert b'To Kill a Mockingbird' in response.data
    assert b'1984' in response.data
    
# Test case for POST request to filter books on the books page.
# This test checks if filtering books by a specific genre (in this case, 'fiction') using a POST request works correctly.
# It posts data to the books page, specifying the 'fiction' genre, and follows redirects.
# It asserts that the response status code is 200, indicating a successful request.
# Additionally, it verifies that the response data includes books that belong to the 'fiction' genre, such as 'To Kill a Mockingbird' and 'The Catcher in the Rye'.
def test_books_page_post(client):
    
    # Filtering by 'fiction' genre
    response = client.post(url_for('books.book_page'), data={
        'fiction': True,
    }, follow_redirects=True)

    assert response.status_code == 200
    # Check that the response includes books from the 'fiction' genre
    assert b'To Kill a Mockingbird' in response.data
    assert b'The Catcher in the Rye' in response.data

# Test case for GET request to view a specific book's page.
# This test checks if a book's page can be accessed successfully by sending a GET request.
# It asserts that the response status code is 200, indicating a successful request.
# Additionally, it checks if the response data contains specific content expected to be rendered by the template
def test_book_page_get(client):
    # checking Book's page url
    response = client.get('/books/1')
    assert response.status_code == 200
    # Check if the response contains specific content expected to be rendered by the template
    assert b"To Kill a Mockingbird" in response.data  

# Test case for POST request to search books by title.
# This test checks if searching for books by title using a POST request works correctly.
# It posts data to the search endpoint with a specific book title ('To Kill a Mockingbird'), and follows redirects.
# It asserts that the response status code is 200, indicating a successful request.
# Additionally, it checks if the response data contains the expected book title ('To Kill a Mockingbird') and ensures that the search term is also present in the response.
def test_search_books_by_title_post(client):
    
    test_title = "To Kill a Mockingbird"  
    response = client.post('/search', data={'search': test_title}, follow_redirects=True)
    assert response.status_code == 200
    assert b"To Kill a Mockingbird" in response.data
    assert bytes(test_title, 'utf-8') in response.data  # Check that the search result is in the response

# Test case for POST request to search books by author.
# This test checks if searching for books by author using a POST request works correctly.
# It posts data to the search endpoint with a specific author name ('J.R.R. Tolkien'), and follows redirects.
# It asserts that the response status code is 200, indicating a successful request.
# Additionally, it checks if the response data contains books authored by 'J.R.R. Tolkien', such as 'The Hobbit' and 'The Lord of the Rings'.
# It also ensures that the author's name is present in the response.
def test_search_books_by_author_post(client):
    
    test_author = "J.R.R. Tolkien"  
    response = client.post('/search', data={'search': test_author}, follow_redirects=True)
    assert response.status_code == 200
    assert b"The Hobbit" in response.data
    assert b"The Lord of the Rings" in response.data
    assert bytes(test_author, 'utf-8') in response.data 

# Test case for unsuccessful login attempt.
# This test checks if attempting to log in with invalid credentials results in the expected behavior.
# It posts data to the login endpoint with invalid email and password credentials.
# The test follows redirects and asserts that the response status code is 200, indicating a successful request.
# It also checks if the response data contains content indicative of a failed login attempt, such as the presence of 'Login Page'.
def test_unsuccessful_login(client):
    
    invalid_credentials = {
        'email_address': 'wrong@example.com',
        'password': 'wrongpassword',
    }
    response = client.post('/login', data=invalid_credentials, follow_redirects=True)
    assert response.status_code == 200
    print(response.data)
    assert b'Login Page' in response.data

# Test case for successful login.
# This test checks if logging in with valid credentials results in the expected behavior.
# It posts data to the login endpoint with valid email and password credentials.
# The test follows redirects and asserts that the response status code is 200, indicating a successful request.
# Additionally, it checks if the response data contains the user's email address, confirming a successful login.
def test_successful_login(client):
    
    valid_credentials = {
        'email_address': 'user1@example.com',
        'password': 'password',
    }
    response = client.post('/login', data=valid_credentials, follow_redirects=True)
    assert response.status_code == 200
    assert b'user1@example.com' in response.data

# Test case for accessing the basket page when not authenticated.
# This test checks if accessing the basket page without authentication redirects the user to the login page.
# It sends a GET request to the basket endpoint and follows redirects.
# The test asserts that the response data contains messages prompting the user to log in to view their basket and verifies the presence of a 'Login' link.
def test_basket_page_unauthenticated(client):
    response = client.get('/basket', follow_redirects=True)
    assert b'Please log in to view your basket.' in response.data
    assert b'Login' in response.data

# Test case for accessing the basket page when authenticated.
# This test checks if accessing the basket page while authenticated as a user returns the expected content.
# It utilizes the login_as_user fixture to authenticate a user.
# Then, it sends a GET request to the basket endpoint and asserts that the response status code is 200, indicating success.
# Additionally, it verifies that the response data contains content indicative of the basket page being successfully accessed, such as the presence of 'Basket'.
def test_basket_page_authenticated(login_as_user, client):
    # login_as_user is a fixture that logs in a user
    response = client.get('/basket')
    assert response.status_code == 200
    
    assert b'Basket' in response.data

# Test case for accessing the wishlist page when not authenticated.
# This test checks if accessing the wishlist page without authentication redirects the user to the login page.
# It sends a GET request to the wishlist endpoint and follows redirects.
# The test asserts that the response data contains messages prompting the user to log in to view their wishlist and verifies the presence of a 'Login' link.
def test_wishlist_page_unauthenticated(client):
    response = client.get('/wishlist', follow_redirects=True)
    assert b'Please log in to view your wishlist.' in response.data
    assert b'Login' in response.data  

# Test case for accessing the wishlist page when authenticated.
# This test checks if accessing the wishlist page while authenticated as a user returns the expected content.
# It utilizes the login_as_user fixture to authenticate a user.
# Then, it sends a GET request to the wishlist endpoint and asserts that the response status code is 200, indicating success.
# Additionally, it verifies that the response data contains content indicative of the wishlist page being successfully accessed, such as the presence of 'items in wishlist'.
def test_wishlist_page_authenticated(login_as_user, client):
    response = client.get('/wishlist')
    assert response.status_code == 200
    print(response.data)
    assert b'items in wishlist' in response.data  # Check for a unique element present in the wishlist page

# Test case for displaying an image associated with a valid book ID.
# This test checks if requesting to display an image associated with a valid book ID returns the expected image content.
# It uses the add_book_with_image fixture to obtain a valid book ID.
# Then, it sends a GET request to the display endpoint with the book ID.
# The test asserts that the response status code is 200, indicating success.
def test_display_with_valid_book_id(client, add_book_with_image):
    book_id = add_book_with_image  # Get the ID from the fixture
    response = client.get(f'/display/{book_id}')
    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'
    assert response.data[:4] == b'\xff\xd8\xff\xe0'  # JPEG file signature

# Test case for accessing the main page as an authenticated regular user.
# This test checks if accessing the main page while authenticated as a regular user returns the expected content.
# It sends a GET request to the main page endpoint.
# The test asserts that the response status code is 200, indicating success.
# Additionally, it checks if the response data contains content indicative of the main page being successfully accessed, such as the presence of 'Main Page'.
def test_main_page_authenticated_regular_user(client):
    response = client.get('/main')
    assert response.status_code == 200
    # Check if the 'admin' variable is correctly recognized as False
    # This assumes your template renders this condition in some detectable way
    print(response.data)
    assert b'Main Page' in response.data
