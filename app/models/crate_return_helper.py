from app.db import db
from app.models.crate_return import CrateReturn
from app.models.crate_return_loader import CrateReturnLoader

def create_crate_return(transporter_id, farmer_id, returned_crates, amount_rupees, loaders):
    crate_return = CrateReturn(
        transporter_id=transporter_id,
        farmer_id=farmer_id,
        returned_crates=returned_crates,
        amount_rupees=amount_rupees
    )
    db.session.add(crate_return)
    db.session.commit()

    for loader in loaders:
        loader_entry = CrateReturnLoader(
            crate_return_id=crate_return.id,
            loader_name=loader['loader_name'],  # ✅ this is the correct key
            per_crate_loading_rupee=loader['per_crate_loading_rupee']
        )
        db.session.add(loader_entry)

    db.session.commit()
    return crate_return
