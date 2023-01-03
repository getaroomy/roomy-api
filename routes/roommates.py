import datetime
from flask import request, jsonify, Blueprint
from firebase_admin import firestore
from models.db import db

roommates_bp = Blueprint('roommates_bp', __name__)

@roommates_bp.route('/get_roommates', methods=['POST','GET'])
def get_roommates():
    """Return all available roommates"""
    try:
        query = db.collection(u'roommates').order_by(u'date', direction=firestore.Query.DESCENDING)
        results = query.stream()
        roommates = []
        ids = []
        for res in results:
            ids.append(res.id)

            # Attach profile pic to posts
            curr_roomy = res.to_dict()
            curr_profile = db.collection(u'profiles').document(curr_roomy[u'poster']).get()
            curr_roomy[u'profilePic'] = curr_profile.to_dict()[u'photoURL']

            roommates.append(curr_roomy)
        return jsonify({"ids": ids, "roommates": roommates}), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400

@roommates_bp.route('/post_roommate', methods=['POST'])
def post_roommate():
    """Request Input: roommate (dictionary)

    Posts single roommate advertisement
    """
    try:
        roommate = request.json
        roommate['date'] = datetime.datetime.utcnow()
        db.collection(u'roommates').add(roommate)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400