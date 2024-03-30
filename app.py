from flask import Flask
from dotenv import load_dotenv
from blueprints.create import client_bp, stylist_bp, auth_bp
import os

from extensions import db

load_dotenv()

app = Flask(__name__)

# print("HERE: " + os.getenv('SQLALCHEMY_DATABASE_URI'))

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

db.init_app(app)

app.register_blueprint(client_bp, url_prefix='/client')
app.register_blueprint(stylist_bp, url_prefix='/stylist')
app.register_blueprint(auth_bp, url_prefix='/auth')

# Add this panrt to run only if this is the main module
if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
        # add_test_table_entry('Hello, this is a test message!')\
        app.run(debug=True)



