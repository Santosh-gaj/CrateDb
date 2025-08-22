from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = "transporter" 

    transporter_id  = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String, nullable=False)  
    contact = db.Column(db.String(20), unique=True, nullable=False)  
    password_hash  = db.Column(db.Text, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hashes the password before storing it."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Checks if the given password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.transporter_id ,
            "name": self.name,
            "contact": self.contact,
            "created_at": self.created_at.isoformat() if self.created_at else None  
        }
