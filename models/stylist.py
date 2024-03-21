from extensions import db

class StylistSpeciality(db.Model):
    __tablename__ = 'STYLIST_SPECIALITIES'

    id = db.Column(db.BigInteger, primary_key=True)
    stylist_id = db.Column(db.BigInteger, db.ForeignKey('STYLIST_TABLE.id'))
    speciality = db.Column(db.BigInteger)

    def __repr__(self):
        return f"<StylistSpeciality {self.speciality}>"

class StylistAddress(db.Model):
    __tablename__ = 'STYLIST_ADDRESSES'

    id = db.Column(db.BigInteger, primary_key=True)
    street = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip_code = db.Column(db.BigInteger)
    country = db.Column(db.Text)
    comfort_radius = db.Column(db.BigInteger)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    stylist_id = db.Column(db.BigInteger, db.ForeignKey('STYLIST_TABLE.id'))

    def __repr__(self):
        return f"<StylistAddress {self.street}, {self.city}, {self.state}>"

class Stylist(db.Model):
    __tablename__ = 'STYLIST_TABLE'

    id = db.Column(db.BigInteger, primary_key=True)  
    fname = db.Column(db.Text) 
    lname = db.Column(db.Text) 
    clients_should_know = db.Column(db.Text)
    addresses = db.relationship('StylistAddress', backref='stylist', lazy=True)
    specialities = db.relationship('StylistSpeciality', backref='stylist', lazy=True)

    def __repr__(self):
        return f"<Stylist {self.fname} {self.lname}>"
