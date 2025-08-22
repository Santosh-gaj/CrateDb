from app.db import db
from app.models.transaction import TransporterFarmerTransaction
from datetime import datetime

def create_transaction(transporter_id, farmer_id, crate_count, amount_rupees):
    # Find the latest transaction for this farmer and transporter
    existing_transaction = (
        db.session.query(TransporterFarmerTransaction)
        .filter_by(transporter_id=transporter_id, farmer_id=farmer_id)
        .order_by(TransporterFarmerTransaction.transaction_date.desc())
        .first()
    )

    if existing_transaction:
        # Just update the existing one
        existing_transaction.crate_count += crate_count
        existing_transaction.amount_rupees += amount_rupees
        existing_transaction.transaction_date = datetime.utcnow()
    else:
        # No transaction found, create a new one
        existing_transaction = TransporterFarmerTransaction(
            transporter_id=transporter_id,
            farmer_id=farmer_id,
            crate_count=crate_count,
            amount_rupees=amount_rupees,
            transaction_date=datetime.utcnow()
        )
        db.session.add(existing_transaction)

    db.session.commit()
