from datetime import datetime, timedelta
import io

from sqlalchemy import extract, func, or_
from application import db
from flask import render_template, redirect, send_file, url_for, flash, request, jsonify, Blueprint
from application.models import Sale, User, Book, Review, Basket, Wishlist
from application.forms import RegisterForm, LoginForm, ReviewForm, AddBookForm, EditBookForm, AddToBasketForm, BookFilterForm, GenreForm
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint("main", __name__)
users = Blueprint("users", __name__)
books = Blueprint("books", __name__)
reviews = Blueprint("reviews", __name__)

@books.route('/books', methods=['GET', 'POST'])
def book_page():
    form = GenreForm()
    if request.method == "GET":
        if current_user.is_authenticated:
            admin_or_not = current_user.is_admin
        else:
            admin_or_not = False
        print(f'admin: {admin_or_not}')
        all_books = Book.query.all()
        return render_template('book.html', books=all_books, admin=admin_or_not, form=form)
    if request.method == "POST":
        if form.validate_on_submit():
            selected_genres = []
            price_conditions = []
            # Check each BooleanField individually
            if form.fiction.data:
                selected_genres.append('fiction')
            if form.non_fiction.data:
                selected_genres.append('non-fiction')
            if form.mystery.data:
                selected_genres.append('mystery')
            if form.science_fiction.data:
                selected_genres.append('science-fiction')
            if form.fantasy.data:
                selected_genres.append('fantasy')
            if form.romance.data:
                selected_genres.append('romance')
            if form.classic.data:
                selected_genres.append('classic')
            if form.thriller.data:
                selected_genres.append('thriller')
            if form.biography.data:
                selected_genres.append('biography')
            if form.history.data:
                selected_genres.append('history')
            if form.self_help.data:
                selected_genres.append('self-help')

            # Check each price range BooleanField
            if form.under5.data:
                price_conditions.append(Book.price < 5)
            if form.filter5_10.data:
                price_conditions.append((Book.price >= 5) & (Book.price <= 10))
            if form.filter10_15.data:
                price_conditions.append((Book.price >= 10) & (Book.price <= 15))
            if form.filter15_20.data:
                price_conditions.append((Book.price >= 15) & (Book.price <= 20))
            if form.filter20_25.data:
                price_conditions.append((Book.price >= 20) & (Book.price <= 25))

            

            print(f'Genres are: {selected_genres}')
            print(f'Price are: {price_conditions}')
            
            query = Book.query
            if selected_genres:
                query = query.filter(Book.genre.in_(selected_genres))
            # Apply the price filters if any
            if price_conditions:
                query = query.filter(or_(*price_conditions))
             # Apply the sorting preferences
            sort_option = form.sorting.data
            if sort_option == 'alphabetical':
                query = query.order_by(Book.title.asc())
            elif sort_option == 'price_low_high':
                query = query.order_by(Book.price.asc())
            elif sort_option == 'price_high_low':
                query = query.order_by(Book.price.desc())
            all_books = query.all()
        else:
            all_books = Book.query.all()

        return render_template('book.html', books=all_books, form=form)

@books.route('/books/<id>', methods=['GET', 'POST'])
def home_page(id):
    form = ReviewForm()
    form2 = AddToBasketForm()
    if request.method == "GET":
        if current_user.is_authenticated:
            admin_or_not = current_user.is_admin
        else:
            admin_or_not = False
        
        book = Book.query.filter_by(id=id).first()
        book_review = Review.query.filter_by(book_id=id).all()

        # Calculate average review rating
        average_rating = 0.0
        total_reviews = len(book_review)

        if total_reviews > 0:
            for review in book_review:
                average_rating += review.rating

            average_rating /= total_reviews

        similar_books = Book.query.filter_by(genre=book.genre).all()
        
        return render_template('individual-book.html', book=book, reviews=book_review, similar_books=similar_books, average_rating=average_rating, form=form, form2=form2, admin=admin_or_not)
    
    if request.method == "POST":
        form_type = request.form.get('form_type')
        current_id = current_user.id
        if form_type == 'add_review':
        
            selected_rating = request.form['rate']
            
            
            if form.validate_on_submit():            
                review_to_create = Review(book_id=id, user_id=current_id, review_text=form.review.data, rating=selected_rating)
                db.session.add(review_to_create)
                db.session.commit()
                flash(f"Review created successfully!", category="success")
            else:
                # Print form errors to identify the issue
                print(form.errors)

                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'There was an error with the field "{field}": {error}', category='danger')

            # Retrieve the book and reviews again after the new review is added
            book = Book.query.filter_by(id=id).first()
            book_review = Review.query.filter_by(book_id=id).all()

            # Calculate average review rating
            average_rating = 0.0
            total_reviews = len(book_review)

            if total_reviews > 0:
                for review in book_review:
                    average_rating += review.rating

                average_rating /= total_reviews

            similar_books = Book.query.filter_by(genre=book.genre).all()

            return render_template('individual-book.html', book=book, reviews=book_review, similar_books=similar_books, average_rating=average_rating, form=form, form2=form2)
        elif request.form['action'] == 'add_to_basket':
            book_quantity = form2.quantity.data
            if book_quantity > 0:
                Basket.add_to_basket(user_id=current_id, book_id=id,quantity=book_quantity)
                flash(f'{book_quantity} items added to basket', category='warning')
                return redirect(url_for('main.basket_page'))
            else:
                flash(f'quantity has to be greater than {book_quantity}', category='danger')

                # Retrieve the book again
                book = Book.query.filter_by(id=id).first()
                book_review = Review.query.filter_by(book_id=id).all()

                # Calculate average review rating
                average_rating = 0.0
                total_reviews = len(book_review)

                if total_reviews > 0:
                    for review in book_review:
                        average_rating += review.rating

                    average_rating /= total_reviews

                similar_books = Book.query.filter_by(genre=book.genre).all()

                return render_template('individual-book.html', book=book, reviews=book_review, similar_books=similar_books, average_rating=average_rating, form=form,form2=form2)
        elif request.form['action'] == 'add_to_wishlist':
            book_quantity = form2.quantity.data
            if book_quantity > 0:
                Wishlist.add_to_wishlist(user_id=current_id, book_id=id,quantity=book_quantity)
                flash(f'{book_quantity} items added to wishlist', category='warning')
                return redirect(url_for('main.wishlist_page'))
            else:
                flash(f'quantity has to be greater than {book_quantity}', category='danger')

                # Retrieve the book again
                book = Book.query.filter_by(id=id).first()
                book_review = Review.query.filter_by(book_id=id).all()

                # Calculate average review rating
                average_rating = 0.0
                total_reviews = len(book_review)

                if total_reviews > 0:
                    for review in book_review:
                        average_rating += review.rating

                    average_rating /= total_reviews

                similar_books = Book.query.filter_by(genre=book.genre).all()

                return render_template('individual-book.html', book=book, reviews=book_review, similar_books=similar_books, average_rating=average_rating, form=form,form2=form2)

@books.route('/search', methods=['GET','POST'])
def search_books():
    if current_user.is_authenticated:
        admin_or_not = current_user.is_admin
    else:
        admin_or_not = False
    query = request.form.get('search')
    similar_books_by_title = Book.query.filter(Book.title.ilike(f'%{query}%')).all()
    similar_books_by_author = Book.query.filter(Book.author.ilike(f'%{query}%')).all()

    return render_template(
        'search_results.html',
        query=query,
        books_by_title=similar_books_by_title,
        books_by_author=similar_books_by_author,
        admin=admin_or_not
    )

@main.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(email_address=form.email_address.data, _password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in!", category="success")

        return redirect(url_for('main.main_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
@main.route('/', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email_address=form.email_address.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            print("hello")
            login_user(attempted_user)
            flash(f'Success! You are logged in!', category='success')
            if attempted_user.is_admin == True:
                #changed from admin to book. main.admin_page
                return redirect(url_for('main.main_page'))
            else:
                return redirect(url_for('main.main_page'))
        else:
            flash('Email and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@main.route('/basket', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def basket_page():
    if request.method == 'GET':
        if current_user.is_authenticated:
            current_id = current_user.id
            
            admin_or_not = current_user.is_admin
        
            items = Basket.get_basket_items(user_id=current_id)
            subtotal = 0
            if items:
                for item in items:
                    
                    subtotal += item.quantity * item.book.price
            return render_template('basket.html', items=items, subtotal = subtotal, admin=admin_or_not)
        else:
            flash('Please log in to view your basket.', 'warning')
            return redirect(url_for('main.login_page'))
    elif request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'delete':
            # Assuming you send the basket_id in the request
            basket_id = int(request.form['basket_id'])
            Basket.remove_from_basket(basket_id)
            flash(f"Item successfully deleted!", category="info")
        elif action == 'checkout':
            current_id = current_user.id
            items = Basket.get_basket_items(user_id=current_id)

            # Update quantities in the database
            try:
                for item in items:
                    book = item.book
                    new_stock = book.stock - item.quantity
                    if new_stock < 0:
                        flash(f"Insufficient stock for {book.title}. Please update your basket.", category="warning")
                        return redirect(url_for('main.basket_page'))

                    book.stock = new_stock
                    db.session.commit()

                # Remove items from the basket after updating quantities
                Basket.clear_basket(user_id=current_id)
                flash("Checkout successful!", category="success")
    
            except:
                flash("An error occurred during checkout. Please try again.", category="danger")

        elif action == 'move_to_wishlist':
            basket_id = int(request.form['basket_id'])
            current_id = current_user.id
            book_id = request.form.get('book_id')
            
            item = Basket.query.filter_by(user_id=current_id, book_id=book_id).first()
            
            # Move the selected item to the wishlist
            Basket.move_to_wishlist(user_id=current_id, book_id=book_id, quantity=item.quantity)
            flash("Item moved to wishlist!", category="success")


        # Retrieve updated basket items
        current_id = current_user.id
        items = Basket.get_basket_items(user_id=current_id)

        subtotal = 0
        if items:
            for item in items:
                subtotal += item.quantity * item.book.price
        return render_template('basket.html', items=items, subtotal = subtotal)
        

@main.route('/wishlist', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def wishlist_page():
    if request.method == 'GET':
        if current_user.is_authenticated:
            current_id = current_user.id
            
            admin_or_not = current_user.is_admin
        
            items = Wishlist.get_wishlist_items(user_id=current_id)
            
            return render_template('wishlist.html', items=items, admin=admin_or_not)
        else:
            flash('Please log in to view your wishlist.', 'warning')
            return redirect(url_for('main.login_page'))
    elif request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'delete':
            # Assuming you send the basket_id in the request
            basket_id = int(request.form['basket_id'])
            Wishlist.remove_from_wishlist(basket_id)
            flash(f"Item successfully deleted!", category="info")
        elif action == 'move_to_wishlist':
            basket_id = int(request.form['basket_id'])
            current_id = current_user.id
            book_id = request.form.get('book_id')
            
            item = Wishlist.query.filter_by(user_id=current_id, book_id=book_id).first()
            
            # Move the selected item to the wishlist
            Wishlist.move_to_basket(user_id=current_id, book_id=book_id, quantity=item.quantity)
            flash("Item moved to wishlist!", category="success")

        if current_user.is_authenticated:
            admin_or_not = current_user.is_admin
        else:
            admin_or_not = False

        # Retrieve updated basket items
        current_id = current_user.id
        items = Wishlist.get_wishlist_items(user_id=current_id)
        return render_template('wishlist.html', items=items, admin=admin_or_not)


@main.route('/admin', methods=['GET', 'POST'])
def admin_page():
    form = AddBookForm()
    form2 = EditBookForm()
    if request.method == 'GET':
        current_id = current_user.id
        attempted_user = User.query.filter_by(id=current_id).first()
        if attempted_user.is_admin:
            admin_or_not=True
            all_books = Book.query.all()
            return render_template('admin2.html', books=all_books, form=form, form2=form2,admin=admin_or_not)
        else:
            return redirect(url_for('books.book_page'))
        
    elif request.method == 'POST':
        form_type = request.form.get('form_type')
         # Check if the form is for editing a book
        if current_user.is_authenticated:
            admin_or_not = current_user.is_admin
        else:
            admin_or_not = False

        if form_type == 'add_record':
            try:
                book = Book(title=form.title.data, price=form.price.data, barcode=form.barcode.data, description=form.description2.data, author=form.author.data, release_year=form.releaseYear.data, genre=form.genre.data, blurb=form.blurb.data, stock=form.stock.data, book_picture=form.book_picture.data.read())

                db.session.add(book)
                db.session.commit()
                flash(f'Successfully added the book.', category='success')
            except Exception as e:
                # Rollback the transaction in case of an error
                db.session.rollback()  
                flash(f'Failed to add the book. Error: {str(e)}', category='danger')
                


            all_books = Book.query.all()
            return render_template('admin2.html', books=all_books, form=form, form2=form2, admin=admin_or_not)

        elif form_type == 'update_record':
            try:
                # Access the book ID
                book_id = int(request.form['edit_book'])

                # Update the book in the database
                book = Book.query.get(book_id)
                book.title = form2.title.data
                book.price = form2.price.data
                book.barcode = form2.barcode.data
                book.description = form2.description2.data
                book.author = form2.author.data
                book.release_year = form2.releaseYear.data
                book.blurb = form2.blurb.data
                book.stock = form2.stock.data

                db.session.commit()

                flash(f'Successfully updated the book', category='success')
            except Exception as e:
                # Rollback the transaction in case of an error
                db.session.rollback()  
                flash(f'Failed to update the book. Error: {str(e)}', category='danger')

            all_books = Book.query.all()
            return render_template('admin2.html', books=all_books, form=form, form2=form2, admin=admin_or_not)
        
        elif form_type == 'delete_record':
            try:
                # Access the book ID
                book_id = request.form['delete_book']
                book_id = int(book_id)

                # Fetch the book by ID
                book = Book.query.get(book_id)

                # Update the delisted property to True
                book.delisted = True

                # Commit the changes to the database
                db.session.commit()

                flash(f'Successfully delisted the book: {book.title}', category='success')
            except Exception as e:
                # Rollback the transaction in case of an error
                db.session.rollback()  
                flash(f'Failed to delist the book. Error: {str(e)}', category='danger')

            all_books = Book.query.all()
            return render_template('admin2.html', books=all_books, form=form, form2=form2, admin=admin_or_not)
        elif form_type == 'relist_record':
            try:
                # Access the book ID
                book_id = request.form['relist_book']
                book_id = int(book_id)

                # Fetch the book by ID
                book = Book.query.get(book_id)

                # Update the delisted property to True
                book.delisted = False

                # Commit the changes to the database
                db.session.commit()

                flash(f'Successfully relisted the book: {book.title}', category='success')
            except Exception as e:
                # Rollback the transaction in case of an error
                db.session.rollback()  
                flash(f'Failed to relist the book. Error: {str(e)}', category='danger')

            all_books = Book.query.all()
            return render_template('admin2.html', books=all_books, form=form, form2=form2, admin=admin_or_not)


@books.route('/display/<int:book_id>')
def display(book_id):
    book = Book.query.get_or_404(book_id)
    return send_file(io.BytesIO(book.book_picture), mimetype='image/jpeg')

@main.route('/update_basket', methods=['POST'])
def update_basket():
    if current_user.is_authenticated:
        basket_id = request.form.get('basket_id')
        new_quantity = request.form.get('quantity')

        # Update the quantity in the database based on basket_id and new_quantity
        Basket.update_quantity(basket_id, new_quantity)

    return redirect(url_for('main.basket_page'))

@main.route('/update_wishlist', methods=['POST'])
def update_wishlist():
    if current_user.is_authenticated:
        basket_id = request.form.get('basket_id')
        new_quantity = request.form.get('quantity')

        # Update the quantity in the database based on basket_id and new_quantity
        Wishlist.update_quantity(basket_id, new_quantity)

    return redirect(url_for('main.wishlist_page'))

@main.route('/main', methods=['GET', 'POST'])
def main_page():
    if current_user.is_authenticated:
        admin_or_not = current_user.is_admin
    else:
        admin_or_not = False
    return render_template('main-page.html', admin=admin_or_not)

@main.route('/statistics', methods=['GET'])
def statistics_page():
    if current_user.is_authenticated:
        admin_or_not = current_user.is_admin
    else:
        admin_or_not = False
    # Query to get books with stock 10 and below
    low_stock_books = Book.query.filter(Book.stock <= 10).all()

    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    # Query to get the top 5 books by revenue in the past month
    book_sales_info = db.session.query(
        Book.title,
        Book.price,
        Book.barcode,
        Book.genre,
        Book.author,
        Book.release_year,
        Book.stock,
        func.sum(Sale.quantity_sold).label('sales'),
        func.sum(Sale.quantity_sold * Book.price).label('revenue')
    ).join(Sale, Book.id == Sale.book_id
    ).filter(extract('month', Sale.sale_date) == current_month,
             extract('year', Sale.sale_date) == current_year
    ).group_by(Book.id
    ).order_by(func.sum(Sale.quantity_sold * Book.price).desc()
    ).limit(5
    ).all()

    return render_template('statistics.html',
                        low_stock_books=low_stock_books, book_sales_info=book_sales_info, admin=admin_or_not)

@main.route('/statistics/revenue-generated')
def statistics_data():

    # Query the database to sum up the revenue per month
    monthly_revenue = db.session.query(
        extract('month', Sale.sale_date).label('month'),
        func.sum(Sale.quantity_sold * Book.price).label('revenue')
    ).join(Book).group_by('month').order_by('month').all()

    # Convert the query result into a dictionary format for labels and values
    labels = []
    values = []
    for month, revenue in monthly_revenue:
        # Assuming 'month' is an integer, convert it to a month name
        month_name = datetime(1900, month, 1).strftime('%B')  # Will give 'January', 'February', etc.
        labels.append(month_name)
        values.append(float(revenue))  # Convert Decimal to float if necessary

    data = {
        'labels': labels,
        'values': values
    }
    return jsonify(data)

@main.route('/statistics/sales-by-genre')
def sales_by_genre_data():
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    # Aggregate sales data by genre for the current month and year
    sales_by_genre = db.session.query(
        Book.genre.label('genre'),
        func.sum(Sale.quantity_sold).label('quantity_sold')
    ).join(Sale, Book.id == Sale.book_id
    ).filter(extract('month', Sale.sale_date) == current_month,
             extract('year', Sale.sale_date) == current_year
    ).group_by(Book.genre
    ).all()

    # Prepare the data for the response
    labels = [result.genre for result in sales_by_genre]
    values = [result.quantity_sold for result in sales_by_genre]

    data = {
        'labels': labels,
        'values': values
    }
    return jsonify(data)

from collections import OrderedDict, defaultdict

@main.route('/statistics/reviews-count')
def reviews_count_data():
    # Calculate the date ranges for the past 7 days and 7-14 days
    end_date = datetime.utcnow()
    start_date_7_days_ago = end_date - timedelta(days=7)
    start_date_14_days_ago = end_date - timedelta(days=14)

    # Query the database to fetch reviews for the past 7 days
    reviews_past_7_days = Review.query.filter(
        Review.date >= start_date_7_days_ago,
        Review.date < end_date
    ).all()

    # Query the database to fetch reviews for the 7-14 day period
    reviews_7_14_days = Review.query.filter(
        Review.date >= start_date_14_days_ago,
        Review.date < start_date_7_days_ago
    ).all()

    # Initialize counters for each star rating
    star_ratings_count_7_days = defaultdict(int)
    star_ratings_count_7_14_days = defaultdict(int)

    # Count the number of reviews for each star rating in the past 7 days
    for review in reviews_past_7_days:
        star_ratings_count_7_days[review.rating] += 1

    # Count the number of reviews for each star rating in the 7-14 day period
    for review in reviews_7_14_days:
        star_ratings_count_7_14_days[review.rating] += 1

# Ensure that all star ratings are included in the dataset
    for i in range(1, 6):
        if i not in star_ratings_count_7_days:
            star_ratings_count_7_days[i] = 0
        if i not in star_ratings_count_7_14_days:
            star_ratings_count_7_14_days[i] = 0

    # Ensure that all star ratings are included in the dataset
    ordered_star_ratings_count_7_days = OrderedDict(sorted(star_ratings_count_7_days.items()))
    ordered_star_ratings_count_7_14_days = OrderedDict(sorted(star_ratings_count_7_14_days.items()))

    # Prepare the data for the response
    labels_7_days = list(ordered_star_ratings_count_7_days.keys())
    values_7_days = list(ordered_star_ratings_count_7_days.values())

    labels_7_14_days = list(ordered_star_ratings_count_7_14_days.keys())
    values_7_14_days = list(ordered_star_ratings_count_7_14_days.values())


    data = {
        'labels_7_days': labels_7_days,
        'values_7_days': values_7_days,
        'labels_7_14_days': labels_7_14_days,
        'values_7_14_days': values_7_14_days,
    }
    return jsonify(data)
