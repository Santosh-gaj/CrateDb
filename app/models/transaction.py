from app.db import db
from datetime import datetime

class TransporterFarmerTransaction(db.Model):
    __tablename__ = 'transporter_farmer_transactions'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    transporter_id = db.Column(db.Integer, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id'), nullable=False)
    crate_count = db.Column(db.Integer, nullable=False)
    amount_rupees = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # farmer = db.relationship('Farmer', backref= db.backref('transactions', lazy=True))