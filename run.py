from application import create_app, db, add_fake_books, add_fake_reviews, add_fake_users, add_fake_sales

app = create_app()
#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
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
    app.run(debug=True)

