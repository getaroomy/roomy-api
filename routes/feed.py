import datetime
from flask import request, jsonify, Blueprint
from firebase_admin import firestore
from models.db import db
from models.wrappers import token_required
from google.cloud.firestore_v1.base_query import FieldFilter

feed_bp = Blueprint('feed_bp', __name__)

@feed_bp.route('/get_feed_posts', methods=['GET'])
@token_required
def get_feed_posts():
    """Return all main page posts"""
    try:
        uid = request.args.get("uid")
        city = request.args.get("city")
        if not city:
            curr_profile = db.collection(u'profiles').document(uid).get()
            city = curr_profile.to_dict()[u'city']
        query = (
            db.collection(u'feed_posts')
            .where(filter=FieldFilter(u'city','==',city))
            .order_by(u'date', direction=firestore.Query.DESCENDING)
            .limit(10)
        )
        results = query.stream()
        posts = []
        for res in results:
            curr_roomy = res.to_dict()
            curr_uid = curr_roomy.get('uid')
            curr_profile = db.collection(u'profiles').document(curr_uid).get()
            curr_roomy['photoURL'] = curr_profile.to_dict()[u'photoURL']
            curr_roomy['displayName'] = curr_profile.to_dict()[u'displayName']
            posts.append(curr_roomy)
        return jsonify({"posts": posts}), 200
    except Exception as e:
        return f"An error occured: {e}", 500

@feed_bp.route('/create_feed_post', methods=['POST'])
@token_required
def create_feed_post():
    """Request Input: article (dictionary)

    Posts single main page post
    """
    try:
        body = request.json
        if not body.get("city"):
            uid = body.get("uid")
            curr_profile = db.collection(u'profiles').document(uid).get()
            body['city'] = curr_profile.to_dict()[u'city']
        db.collection(u'feed_posts').add(body)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An error occured: {e}", 500
