from app.db import db
from datetime import datetime

class Farmer(db.Model):
    __tablename__ = 'farmers'
    
    farmer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    transporter_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    transactions = db.relationship('TransporterFarmerTransaction', backref='farmer', lazy=True)