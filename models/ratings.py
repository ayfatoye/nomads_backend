from extensions import db

class Rating(db.Model):
    __tablename__ = 'STYLIST_RATINGS'
    id = db.Column(db.BigInteger, primary_key=True)
    stylist_id = db.Column(db.BigInteger, db.ForeignKey('STYLIST_TABLE.id'), nullable=False)
    client_id = db.Column(db.BigInteger, nullable=False)
    review = db.Column(db.Text)
    stars = db.Column(db.Float)

    def __repr__(self):
        return f"<Rating {self.id}>"


class RatingTag(db.Model):
    __tablename__ = 'STYLIST_RATING_TAGS'
    id = db.Column(db.BigInteger, primary_key=True)
    rating_id = db.Column(db.BigInteger, db.ForeignKey('STYLIST_RATINGS.id'), nullable=False)
    tag = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f"<RatingTag {self.id}>"