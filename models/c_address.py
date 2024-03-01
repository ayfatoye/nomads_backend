from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ClientAddress(db.Model):
    __tablename__ = 'CLIENT_ADDRESSES'

    id = db.Column(db.BigInteger, primary_key=True)
    street = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip_code = db.Column(db.BigInteger)
    country = db.Column(db.Text)
    comfort_radius = db.Column(db.BigInteger)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)

    def __repr__(self):
        return f"<ClientAddress {self.street}, {self.city}, {self.state}>"