from app.models.farmer import Farmer
from app.db import db
from app.models.transaction import TransporterFarmerTransaction
from app.models.crate_return import CrateReturn
from sqlalchemy import func

def find_or_create_farmer_by_name(name, transporter_id):
    farmer = Farmer.query.filter_by(name=name, transporter_id=transporter_id).first()
    if farmer:
        return farmer
    
    new_farmer = Farmer(name=name, transporter_id=transporter_id)
    db.session.add(new_farmer)
    db.session.commit()
    return new_farmer


def get_farmers_with_total_crates(transporter_id):
    given_crates = db.session.query(
        Farmer.farmer_id,
        Farmer.name,
        func.sum(TransporterFarmerTransaction.crate_count).label('total_given')
    ).join(TransporterFarmerTransaction).filter(
        Farmer.transporter_id == transporter_id
    ).group_by(Farmer.farmer_id, Farmer.name).all()

    returned_crates = db.session.query(
        CrateReturn.farmer_id,
        func.sum(CrateReturn.returned_crates).label('total_returned')
    ).filter(CrateReturn.transporter_id == transporter_id).group_by(CrateReturn.farmer_id).all()

    returned_dict = {farmer_id: returned for farmer_id, returned in returned_crates}

    summary = []
    for farmer_id, name, given in given_crates:
        returned = returned_dict.get(farmer_id, 0)
        remaining = given - returned
        summary.append({
            "farmer_name": name,
            "total_given": given,
            "total_returned": returned,
            "remaining": remaining
        })

    return summary


def get_farmer_total_given_crates(transporter_id, farmer_id):
    print(f"Querying total crates given for transporter_id: {transporter_id}, farmer_id: {farmer_id}")
    
    # Correct the filter to ensure the ids are not reversed
    result = db.session.query(
        func.coalesce(TransporterFarmerTransaction.crate_count, 0)
    ).filter(
        TransporterFarmerTransaction.transporter_id == transporter_id,  # Swap these
        TransporterFarmerTransaction.farmer_id == farmer_id   # Swap these
    ).scalar()

    # Debugging output to check result
    if result is None:
        print(f"No crates found for farmer {farmer_id} with transporter {transporter_id}")
    else:
        print(f"Total crates given: {result}")

    return result or 0

def get_farmer_total_returned_crates(transporter_id, farmer_id):
    print(f"Querying total crates returned for farmer_id: {farmer_id}, transporter_id: {transporter_id}")
    result = db.session.query(
        func.sum(CrateReturn.returned_crates)
    ).filter_by(transporter_id=transporter_id, farmer_id=farmer_id).scalar()

    if result is None:
        print(f"No returned crates found for farmer {farmer_id} with transporter {transporter_id}")
    else:
        print(f"Total crates returned: {result}")

    return result or 0