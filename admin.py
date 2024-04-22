from main import User
from main import db

# Function to add a new user
def add_new_user(author, email, password, user_type):
    new_user = User(author=author, email=email, password=password, user_type=user_type)
    db.session.add(new_user)
    db.session.commit()
    return new_user

admin_user = User.query.filter_by(email='admin@example.com').first()



password = "pbkdf2:sha256:600000$xdvNsZfR$29355d8077747b28f0ed8df56d7b22c4d690a95007b8b92a17a72239a38af5c5"