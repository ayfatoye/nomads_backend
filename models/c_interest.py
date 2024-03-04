from extensions import db

class ClientInterest(db.Model):
    __tablename__ = 'CLIENT_INTERESTS'

    id = db.Column(db.BigInteger, primary_key=True)
    hair_id = db.Column(db.BigInteger, db.ForeignKey('CLIENT_HAIRID.id'))
    interest = db.Column(db.BigInteger)

    def __repr__(self):
        return f"<ClientInterest {self.interest}>"