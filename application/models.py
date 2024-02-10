from datetime import datetime
from application import db, bcrypt, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import joinedload

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email_address = db.Column(db.String(length=50), nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)

    @property
    def password(self):
        return self.password

    @password.setter
    def _password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    

class Book(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(length=50), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False)
    author = db.Column(db.String(length=50), nullable=False)
    release_year = db.Column(db.Integer(), nullable=False)
    genre = db.Column(db.String(length=50), nullable=False)
    blurb = db.Column(db.String(length=200), nullable=False)
    stock = db.Column(db.Integer(), nullable=False)
    book_picture = db.Column(db.LargeBinary, nullable=True)
    delisted = db.Column(db.Boolean(), nullable=False, default=False)
    
    def __repr__(self):
        return f'Item {self.title}'
    



class Review(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    book_id = db.Column(db.Integer(), db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    review_text = db.Column(db.String(length=250), nullable=False)
    rating = db.Column(db.Integer(), default=False, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Define relationships
    book = db.relationship('Book', backref=db.backref('reviews', lazy=True))
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    # Define relationships
    book = db.relationship('Book', backref=db.backref('baskets', lazy=True))
    user = db.relationship('User', backref=db.backref('baskets', lazy=True))

    def get_basket_items(user_id):
        return Basket.query.filter_by(user_id=user_id).options(joinedload(Basket.book)).all()

    def add_to_basket(user_id, book_id, quantity):
        # Check if the item already exists in the basket
        existing_item = Basket.query.filter_by(user_id=user_id, book_id=book_id).first()

        if existing_item:
            # Item exists, update the quantity
            existing_item.quantity += quantity
        else:
            # Item does not exist, create a new record
            basket_item = Basket(user_id=user_id, book_id=book_id, quantity=quantity)
            db.session.add(basket_item)

        db.session.commit()

    def update_quantity(basket_id, new_quantity):
        basket_item = Basket.query.get(basket_id)
        basket_item.quantity = new_quantity
        db.session.commit()

    def remove_from_basket(basket_id):
        basket_item = Basket.query.get(basket_id)
        db.session.delete(basket_item)
        db.session.commit()

    def clear_basket(user_id):
        # Remove all items from the user's basket
        basket_items = Basket.query.filter_by(user_id=user_id).all()
        for item in basket_items:
            db.session.delete(item)
        db.session.commit()

    def move_to_wishlist(user_id, book_id, quantity):
        # Check if the item already exists in the wishlist
        existing_item = Wishlist.query.filter_by(user_id=user_id, book_id=book_id).first()

        if not existing_item:
            # Item does not exist in the wishlist, move it
            wishlist_item = Wishlist(user_id=user_id, book_id=book_id, quantity=quantity)
            db.session.add(wishlist_item)
        else:
            existing_item.quantity += quantity
        # Remove the item from the basket
        basket_item = Basket.query.filter_by(user_id=user_id, book_id=book_id).first()
        if basket_item:
            db.session.delete(basket_item)

        db.session.commit()

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    # Define relationships
    book = db.relationship('Book', backref=db.backref('wishlists', lazy=True))
    user = db.relationship('User', backref=db.backref('wishlists', lazy=True))

    def get_wishlist_items(user_id):
        return Wishlist.query.filter_by(user_id=user_id).options(joinedload(Wishlist.book)).all()

    def add_to_wishlist(user_id, book_id, quantity):
        # Check if the item already exists in the wishlist
        existing_item = Wishlist.query.filter_by(user_id=user_id, book_id=book_id).first()

        if existing_item:
            # Item exists, update the quantity
            existing_item.quantity += quantity
        else:
            # Item does not exist, create a new record
            wishlist_item = Wishlist(user_id=user_id, book_id=book_id, quantity=quantity)
            db.session.add(wishlist_item)

        db.session.commit()

    def update_quantity(wishlist_id, new_quantity):
        wishlist_item = Wishlist.query.get(wishlist_id)
        wishlist_item.quantity = new_quantity
        db.session.commit()

    def remove_from_wishlist(wishlist_id):
        wishlist_item = Wishlist.query.get(wishlist_id)
        db.session.delete(wishlist_item)
        db.session.commit()

    def clear_wishlist(user_id):
        # Remove all items from the user's wishlist
        wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
        for item in wishlist_items:
            db.session.delete(item)
        db.session.commit()

    def move_to_basket(user_id, book_id, quantity):
        # Check if the item already exists in the basket
        existing_item = Basket.query.filter_by(user_id=user_id, book_id=book_id).first()

        if not existing_item:
            # Item does not exist in the basket, move it
            basket_item = Basket(user_id=user_id, book_id=book_id, quantity=quantity)
            db.session.add(basket_item)
        else:
            existing_item.quantity += quantity
        # Remove the item from the wishlist
        wishlist_item = Wishlist.query.filter_by(user_id=user_id, book_id=book_id).first()
        if wishlist_item:
            db.session.delete(wishlist_item)

        db.session.commit()

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to the Book model
    book = db.relationship('Book', backref='sales')
    
    @property
    def revenue(self):
        return self.quantity_sold * self.book.price
