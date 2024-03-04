from flask import Flask
from blueprints.client.client import client_bp
# from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
database_name = os.getenv('DATABASE_NAME')
database_user = os.getenv('DATABASE_USER')
database_password = os.getenv('DATABASE_PASSWORD')
database_host = os.getenv('DATABASE_HOST')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{database_user}:{database_password}@{database_host}/{database_name}'

# db = SQLAlchemy(app)

app.register_blueprint(client_bp)

if __name__ == '__main__':
    app.run(debug=True)