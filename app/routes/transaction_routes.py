from flask import Blueprint, request, jsonify
from app.models.farmer_helper import find_or_create_farmer_by_name
from app.models.transaction_helper import create_transaction
from app.models.crate_return import CrateReturn
from app.utils.auth import token_required
from app.models.farmer_helper import get_farmers_with_total_crates
from app.models.transaction import TransporterFarmerTransaction
from app.models.farmer import Farmer
from sqlalchemy import func, desc
from app.db import db

transaction_bp = Blueprint('transaction_bp', __name__, url_prefix='/transactions')

@transaction_bp.route('/create-transaction', methods=['POST'])
@token_required
def create_transaction_api():
    data = request.get_json()
    
    farmer_name = data.get('farmer_name')
    crate_count = data.get('crate_count')
    amount_rupees = data.get('amount_rupees')
    transporter_id = request.transporter_id
    
    if farmer_name is None or crate_count is None or amount_rupees is None or transporter_id is None:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        farmer = find_or_create_farmer_by_name(farmer_name, transporter_id)
        create_transaction(transporter_id, farmer.farmer_id, crate_count, amount_rupees)
        return jsonify({'message': 'Crate successfully given'}), 201
    except Exception as e:
        return jsonify({'message': 'Error: ' + str(e)}), 500


@transaction_bp.route('/farmer-crate-summary', methods=['GET'])
@token_required
def get_farmer_crate_summary():
    try:
        transporter_id = request.transporter_id
        summary = get_farmers_with_total_crates(transporter_id)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
def get_farmers_with_total_crates(transporter_id):
    # Subquery: Get farmers who already returned crates
    returned_farmers_subq = (
        db.session.query(CrateReturn.farmer_id)
        .filter(CrateReturn.transporter_id == transporter_id)
        .distinct()
        .subquery()
    )

    # Main Query: Get farmers who received crates and NOT in returned list
    subquery = (
        db.session.query(
            TransporterFarmerTransaction.farmer_id,
            func.max(TransporterFarmerTransaction.transaction_date).label("latest_transaction")
        )
        .filter(TransporterFarmerTransaction.transporter_id == transporter_id)
        .group_by(TransporterFarmerTransaction.farmer_id)
        .subquery()
    )

    results = (
        db.session.query(
            Farmer.farmer_id,
            Farmer.name,
            func.sum(TransporterFarmerTransaction.crate_count).label("total_given"),
            subquery.c.latest_transaction
        )
        .join(TransporterFarmerTransaction, Farmer.farmer_id == TransporterFarmerTransaction.farmer_id)
        .join(subquery, subquery.c.farmer_id == Farmer.farmer_id)
        .filter(TransporterFarmerTransaction.transporter_id == transporter_id)
        .filter(~Farmer.farmer_id.in_(returned_farmers_subq))
        .group_by(Farmer.farmer_id, Farmer.name, subquery.c.latest_transaction)
        .order_by(desc(subquery.c.latest_transaction))
        .all()
    )

    return [
        {
            "farmer_id": row.farmer_id,
            "farmer_name": row.name,
            "total_given": int(row.total_given)
        }
        for row in results
    ]
