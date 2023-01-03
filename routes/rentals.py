import datetime
from flask import request, jsonify, Blueprint
from firebase_admin import firestore
from models.db import db

rentals_bp = Blueprint('rentals_bp', __name__)

@rentals_bp.route('/get_rentals', methods=['POST','GET'])
def get_rentals():
    """Return all available rentals, 25 at a time"""
    try:
        query = db.collection(u'rentals').order_by(u'date', direction=firestore.Query.DESCENDING).limit(25)
        last_post_id = request.form.get('last_post')
        if last_post_id and len(last_post_id) > 0:
            last_snapshot = db.collection(u'rentals').document(last_post_id).get()
            query = query.start_at(last_snapshot)
        results = query.stream()
        rentals = []
        ids = []
        for res in results:
            if res:
                ids.append(res.id)
                # Attach profile pic to posts
                curr_rental = res.to_dict()
                curr_profile = db.collection(u'profiles').document(curr_rental[u'poster']).get()
                curr_rental[u'profilePic'] = curr_profile.to_dict()[u'photoURL']

                rentals.append(curr_rental)
        return jsonify({"ids": ids, "rentals": rentals}), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400

@rentals_bp.route('/post_rental', methods=['POST'])
def post_rental():
    """Request Input: rental (dictionary)

    Posts single rental advertisement
    """
    try:
        rental = request.json
        rental['date'] = datetime.datetime.utcnow()
        db.collection(u'rentals').add(rental)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400

@rentals_bp.route('/save_property', methods=['POST'])
def save_property():
    """Request Input: uid (string), key (string), save (string)

    Add / remove given property from user saved property list
    """
    try:
        info = request.json
        uid = info['uid']
        key = info['key']
        save = info['save']
        if(save == 'True'):
            db.collection(u'profiles').document(uid).update({
                u'savedProperties': firestore.ArrayUnion([key])
            })
        else:
            db.collection(u'profiles').document(uid).update({
                u'savedProperties': firestore.ArrayRemove([key])
            })
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400