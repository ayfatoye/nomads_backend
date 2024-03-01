from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)  
    hair_id = db.Column(db.BigInteger, db.ForeignKey('hair.id'))  
    address_id = db.Column(db.BigInteger, db.ForeignKey('address.id'))  
    fname = db.Column(db.Text) 
    lname = db.Column(db.Text) 
    ethnicity = db.Column(db.Text)  
    stylist_should_know = db.Column(db.Text)

    def __repr__(self):
        return f"<Client {self.fname} {self.lname}>"

