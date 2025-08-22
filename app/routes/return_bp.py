from flask import Blueprint, request, jsonify
from app.models.crate_return_helper import create_crate_return
from app.utils.auth import token_required
from app.models.farmer_helper import get_farmer_total_given_crates, get_farmer_total_returned_crates
from app.models.crate_return import CrateReturn
from app.models.crate_return_loader import CrateReturnLoader

return_bp = Blueprint('return_bp', __name__, url_prefix='/returns')

@return_bp.route('/create', methods=['POST'])
@token_required
def create_return():
    data = request.get_json()

    farmer_id = data.get('farmer_id')
    returned_crates = data.get('returned_crates')
    per_crate_loading_rupee = data.get('per_crate_loading_rupee')
    loaders = data.get('loaders')
    transporter_id = request.transporter_id

    if not all([farmer_id, returned_crates, per_crate_loading_rupee, loaders]):
        return jsonify({'message': 'Missing required fields'}), 400

    total_given = get_farmer_total_given_crates(transporter_id, farmer_id)
    print(f"Total crates given: {total_given}")

    # Check if returned crates are greater than given crates
    if returned_crates > total_given:
        return jsonify({
            'message': 'Return count exceeds total crates given to this farmer.',
            'crates_given': total_given,
            'attempted_return': returned_crates
        }), 400
    
    amount_rupees = returned_crates * per_crate_loading_rupee

    # Assign same loading rupee to each loader
    for loader in loaders:
        loader['per_crate_loading_rupee'] = per_crate_loading_rupee

    try:
        crate_return = create_crate_return(
            transporter_id, farmer_id, returned_crates, amount_rupees, loaders
        )
        return jsonify({
            'message': 'Crate return recorded successfully',
            'crate_return_id': crate_return.id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@return_bp.route('/detailed-summary', methods=['GET'])
@token_required
def get_detailed_return_summary():
    transporter_id = request.transporter_id

    crate_returns = CrateReturn.query.filter_by(transporter_id=transporter_id).all()
    result = []

    for cr in crate_returns:
        loaders = CrateReturnLoader.query.filter_by(crate_return_id=cr.id).all()
        num_loaders = len(loaders)
        crates_per_loader = cr.returned_crates // num_loaders if num_loaders else 0

        # Grouping loaders by per_crate_loading_rupee
        grouped = {}
        for loader in loaders:
            key = loader.per_crate_loading_rupee
            if key not in grouped:
                grouped[key] = {
                    "loader_names": [],
                    "total_loader_amount": 0
                }
            grouped[key]["loader_names"].append(loader.loader_name)
            for key in grouped:
                grouped[key]["total_loader_amount"] = cr.returned_crates * key

        loader_summary = []
        for rupee, data in grouped.items():
            loader_summary.append({
                "loader_name": ", ".join(data["loader_names"]),
                "per_crate_loading_rupee": rupee,
                "total_loader_amount": data["total_loader_amount"]
            })

        result.append({
            "farmer_name": cr.farmer.name,
            "returned_crates": cr.returned_crates,
            "per_crate_farmer_amount": cr.amount_rupees,
            "total_farmer_amount": cr.returned_crates * cr.amount_rupees,
            "loaders": loader_summary
        })

    return jsonify(result), 200


@return_bp.route('/unique-loaders-detailed', methods=['GET'])
@token_required
def get_unique_loaders_detailed():
    transporter_id = request.transporter_id

    crate_returns = CrateReturn.query.filter_by(transporter_id=transporter_id).all()

    loader_stats = {}

    for cr in crate_returns:
        loaders = CrateReturnLoader.query.filter_by(crate_return_id=cr.id).all()
        num_loaders = len(loaders)
        crates_per_loader = cr.returned_crates // num_loaders if num_loaders else 0

        for loader in loaders:
            name = loader.loader_name
            if name not in loader_stats:
                loader_stats[name] = {
                    "loader_name": name,
                    "per_crate_loading_rupee": loader.per_crate_loading_rupee,
                    "total_crates_loaded": 0,
                    "total_amount": 0,
                    "farmers_loaded_for": set()  
                }

            loader_stats[name]["total_crates_loaded"] += crates_per_loader
            loader_stats[name]["total_amount"] += crates_per_loader * loader.per_crate_loading_rupee
            loader_stats[name]["farmers_loaded_for"].add(cr.farmer.name)

    # Convert sets to lists for JSON serialization
    for loader in loader_stats.values():
        loader["farmers_loaded_for"] = list(loader["farmers_loaded_for"])

    return jsonify(list(loader_stats.values())), 200
