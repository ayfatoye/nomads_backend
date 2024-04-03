from extensions import db

class UidToUserId(db.Model):
    __tablename__ = 'UID_TO_USERID'

    id = db.Column(db.BigInteger, primary_key=True)
    uid = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('CLIENT_TABLE.id'), nullable=False)
    user_type = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<UidToUserId {self.id}>"