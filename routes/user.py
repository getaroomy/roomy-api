from flask import request, jsonify, Blueprint
from firebase_admin import firestore
from models.db import db

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/get_other_user', methods=['POST','GET'])
def get_other_user():
    """Request Input: uid (string)
    
    Return other person's profile data on profile page
    """
    try:
        raw_profile = db.collection(u'profiles').document(request.form['uid']).get()
        profile = raw_profile.to_dict()
        for res in profile.get('experiences'): # Attach profile pics to experiences
            uid = res.get('uid')
            curr_profile = db.collection(u'profiles').document(uid).get()
            res['profilePic'] = curr_profile.to_dict()[u'photoURL']
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400

@users_bp.route('/set_user_info', methods=['POST'])
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
        return jsonify({f"An error occured: {e}"}), 400

@users_bp.route('/update_profile_data', methods=['POST'])
def update_profile_data():
    """Request Input: user_info (dictionary)

    Update existing user info
    """
    try:
        info = request.json
        uid = info['uid']
        profile = info['profile']
        db.collection(u'profiles').document(uid).update(profile)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400

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
        return jsonify({f"An error occured: {e}"}), 400