from flask import request, jsonify, Blueprint
from firebase_admin import firestore
from models.db import db
from models.wrappers import token_required
users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/get_my_profile', methods=['GET'])
@token_required
def get_my_profile():
    """Request Input: uid (string)
    
    Return other person's profile data on profile page
    """
    try:
        url_uid = request.args.get("uid")
        print(url_uid)
        raw_profile = db.collection(u'profiles').document(url_uid).get()
        if raw_profile.exists:
            profile = raw_profile.to_dict()
            return jsonify(profile), 200
        else:
            return "User not found", 404
    except Exception as e:
        return f"An error occured: {e}", 500
    
@users_bp.route('/get_other_user_profile', methods=['GET'])
@token_required
def get_other_user_profile():
    """Request Input: uid (string)
    
    Return other person's profile data on profile page
    """
    try:
        url_uid = request.args.get("uid")
        print(url_uid)
        raw_profile = db.collection(u'profiles').document(url_uid).get()
        if raw_profile.exists:
            profile = raw_profile.to_dict()
            if not profile["showPhoneNumber"]:
                profile["phoneNumber"] = ""
            for res in profile.get('experiences'): # Attach profile pics to experiences
                uid = res.get('uid')
                curr_profile = db.collection(u'profiles').document(uid).get()
                res['photoURL'] = curr_profile.to_dict()[u'photoURL']
            return jsonify(profile), 200
        else:
            return "User not found", 404
    except Exception as e:
        return f"An error occured: {e}", 500

@users_bp.route('/set_user_info', methods=['POST'])
@token_required
def set_user_info():
    """Request Input: user_info (dictionary)

    Initially set user info when first creating account
    """
    try:
        info = request.json
        uid = info['uid']
        db.collection(u'profiles').document(uid).set(info)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An error occured: {e}", 500

@users_bp.route('/update_profile_data', methods=['POST'])
@token_required
def update_profile_data():
    """Request Input: user_info (dictionary)

    Update existing user info
    """
    try:
        info = request.json
        uid = info.get('uid')
        db.collection(u'profiles').document(uid).update(info)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An error occured: {e}", 500

@users_bp.route('/post_experience', methods=['POST'])
def post_experience():
    """Request Input: target_uid (string), exp (dictionary)

    Add experience with another user
    """
    try:
        info = request.json
        target_uid = info['target_uid']
        exp = info['exp']
        db.collection(u'profiles').document(target_uid).update({
            u'experiences': firestore.ArrayUnion([exp])
        })
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An error occured: {e}", 500