from app.db import db
from datetime import datetime

class CrateReturn(db.Model):
    __tablename__ = 'crate_returns'

    id = db.Column(db.Integer, primary_key=True)
    transporter_id = db.Column(db.Integer, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id'), nullable=False)
    returned_crates = db.Column(db.Integer, nullable=False)
    amount_rupees = db.Column(db.Float, nullable=False)
    return_date = db.Column(db.Date, default=db.func.current_date())

    # 🔥 Relationship
    farmer = db.relationship('Farmer', backref='crate_returns')