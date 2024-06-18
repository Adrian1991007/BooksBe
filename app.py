from init import create_app, feed_db
from extensions import db

app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        feed_db()
        app.run()
