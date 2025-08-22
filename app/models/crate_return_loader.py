from app.db import db

class CrateReturnLoader(db.Model):
    __tablename__ = 'crate_return_loaders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    crate_return_id = db.Column(db.Integer, db.ForeignKey('crate_returns.id'), nullable=False)
    loader_name = db.Column(db.String(100), nullable=False)
    per_crate_loading_rupee = db.Column(db.Float, nullable=False)