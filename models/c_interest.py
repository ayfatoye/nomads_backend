from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ClientInterest(db.Model):
    __tablename__ = 'CLIENT_INTERESTS'

    id = db.Column(db.BigInteger, primary_key=True)
    hair_id = db.Column(db.BigInteger, db.ForeignKey('hair_profile.id'))
    interest = db.Column(db.BigInteger)

    def __repr__(self):
        return f"<ClientInterest {self.interest}>"