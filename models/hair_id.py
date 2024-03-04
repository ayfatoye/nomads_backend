from extensions import db

class HairProfile(db.Model):
    __tablename__ = 'CLIENT_HAIRID'

    id = db.Column(db.BigInteger, primary_key=True)
    thickness = db.Column(db.BigInteger)
    hair_type = db.Column(db.BigInteger)
    hair_gender = db.Column(db.BigInteger)
    color_level = db.Column(db.BigInteger)
    color_hist = db.Column(db.Text)

    def __repr__(self):
        return f"<HairProfile {self.id}>"