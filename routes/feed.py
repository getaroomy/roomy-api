import datetime
from flask import request, jsonify, Blueprint
from firebase_admin import firestore
from models.db import db

feed_bp = Blueprint('feed_bp', __name__)

@feed_bp.route('/get_articles', methods=['POST','GET'])
def get_articles():
    """Return all main page posts"""
    try:
        query = db.collection(u'articles').order_by(u'actor.date', direction=firestore.Query.DESCENDING).limit(10)
        last_post_id = request.form.get('last_post')
        if last_post_id:
            last_snapshot = db.collection(u'articles').document(last_post_id).get()
            query = query.start_after(last_snapshot)
        results = query.stream()
        posts = []
        ids = []
        for res in results:
            ids.append(res.id)
            curr_post = res.to_dict()
            posts.append(curr_post)
        return jsonify({"ids": ids, "posts": posts}), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400

@feed_bp.route('/get_single_article', methods=['POST','GET'])
def get_single_article():
    """Request Input: pid (string)

    Return single main page post
    """
    try:
        pid = request.form['pid']
        curr_post = db.collection(u'articles').document(pid).get()
        post = curr_post.to_dict()
        return jsonify({"ids":curr_post.id, "posts":post }), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400

@feed_bp.route('/post_article', methods=['POST'])
def post_article():
    """Request Input: article (dictionary)

    Posts single main page post
    """
    try:
        article = request.json
        article['actor']['date'] = datetime.datetime.utcnow() # UTC time added here to avoid JSON misformatting
        db.collection(u'articles').add(article)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400

@feed_bp.route('/update_article', methods=['POST'])
def update_article():
    """Request Input: article_info (dictionary)

    Update existing post on main page
    """
    try:
        info = request.json
        pid = info['pid']
        update = info['update']
        db.collection(u'articles').document(pid).update(update)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({f"An error occured: {e}"}), 400


