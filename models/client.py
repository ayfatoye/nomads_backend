from extensions import db

class Client(db.Model):
    __tablename__ = 'CLIENT_TABLE'

    id = db.Column(db.BigInteger, primary_key=True)  
    hair_id = db.Column(db.BigInteger, db.ForeignKey('CLIENT_HAIRID.id'))  
    address_id = db.Column(db.BigInteger, db.ForeignKey('CLIENT_HAIRID.id'))  
    fname = db.Column(db.Text) 
    lname = db.Column(db.Text) 
    ethnicity = db.Column(db.JSON)  
    stylists_should_know = db.Column(db.Text)

    def __repr__(self):
        return f"<Client {self.fname} {self.lname}>"

class ClientFavourite(db.Model):
    __tablename__ = 'CLIENT_FAVOURITES'
    
    id = db.Column(db.BigInteger, primary_key=True) 
    client_id = db.Column(db.BigInteger, db.ForeignKey('CLIENT_TABLE.id'), nullable=False)
    stylist_id = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f"<ClientFavourite client_id={self.client_id} stylist_id={self.stylist_id}>"