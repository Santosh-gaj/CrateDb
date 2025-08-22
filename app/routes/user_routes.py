from flask import Blueprint, request, jsonify
from app.models.user import User
from app.db import db
import random
import jwt
from datetime import datetime, timedelta
from app.config import  config

# Temporary storage for OTPs (Use Redis or DB in production)
otp_storage = {}

user_routes = Blueprint("user_routes", __name__)

# register api
@user_routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    name = data.get("name")
    contact = data.get("contact")
    password = data.get("password")
    
    if not name or not contact or not password:
        return jsonify({"error": "Name contact and password are required"}), 400
    
    existing_user = User.query.filter_by(contact=contact).first()
    if existing_user:
        return jsonify({"error": "user already registerd"}), 409

    new_user = User(name=name, contact=contact)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User Registerd Sucessfully", "User": new_user.to_dict()}), 201
    

# login api
@user_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    contact = data.get("contact")
    password = data.get("password")

    if not contact or not password:
        return jsonify({"error": "Contact and password are required"}), 400
    
    
    user = User.query.filter_by(contact=contact).first()
   
    if user and user.check_password(password):
        payload = {
            "sub": str(user.transporter_id),
            "exp": datetime.utcnow() + timedelta(hours=4)
        }
        
        token  = jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            "message": "Login Successful",
            "user": user.to_dict(),
            "token": token
        }), 200
    else:
        return jsonify({"error": "Invalid contact or password"}), 401    


# forgot password
# Step 1: Request OTP
@user_routes.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    contact = data.get("contact")

    if not contact:
        return jsonify({"error": "Contact is required"}), 400

    user = User.query.filter_by(contact=contact).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Store OTP temporarily with expiration (5 minutes)
    otp_storage[contact] = {
        "otp": otp,
        "verified": False,
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "user_id": user.transporter_id  # Store user ID for password reset
    }

    # In a real-world scenario, send the OTP via SMS or email
    print(f"OTP for {contact}: {otp}")  # Debugging (Replace with actual SMS service)

    return jsonify({"message": "OTP sent successfully", "otp" : otp}), 200

# Step 2: Verify OTP
@user_routes.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    contact = data.get("contact")
    otp = data.get("otp")

    if not contact or not otp:
        return jsonify({"error": "Contact and OTP are required"}), 400

    stored_otp_data = otp_storage.get(contact)

    if not stored_otp_data:
        return jsonify({"error": "OTP not requested or expired"}), 400

    if stored_otp_data["otp"] != otp:
        return jsonify({"error": "Incorrect OTP"}), 400

    if stored_otp_data["expires_at"] < datetime.utcnow():
        return jsonify({"error": "OTP expired"}), 400

    # Mark OTP as verified
    otp_storage[contact]["verified"] = True

    return jsonify({"message": "OTP verified successfully"}), 200

# Step 3: Reset Password (Only New Password Required)
@user_routes.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    new_password = data.get("new_password")
    contact = data.get("contact")

    if not new_password or not contact:
        return jsonify({"error": "New password and contact are required"}), 400

    # Ensure the contact matches the verified contact
    verified_details = otp_storage.get(contact)
    if not verified_details or not verified_details.get("verified"):
        return jsonify({"error": "OTP not verified for this contact"}), 400

    # Get the correct user ID (only allow reset for the verified user)
    user_id = verified_details.get("user_id")

    # Ensure the request is coming from the correct user
    if user_id is None:
        return jsonify({"error": "Unauthorized password reset attempt"}), 403

    # Find the user
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update password
    user.set_password(new_password)
    db.session.commit()

    # Remove OTP after successful reset
    del otp_storage[contact]

    return jsonify({"message": "Password reset successful"}), 200

