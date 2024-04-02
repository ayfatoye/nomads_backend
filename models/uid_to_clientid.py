from extensions import db

class UidToClientId(db.Model):
    __tablename__ = 'UID_TO_CLIENTID'

    id = db.Column(db.BigInteger, primary_key=True)
    uid = db.Column(db.Text, nullable=False)
    client_id = db.Column(db.BigInteger, db.ForeignKey('CLIENT_TABLE.id'), nullable=False)

    def __repr__(self):
        return f"<UidToClientId {self.id}>"