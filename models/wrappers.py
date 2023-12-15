from functools import wraps
from flask import request
from firebase_admin import auth

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            idToken = auth.verify_id_token(id_token=token)
            if idToken is None:
                return {"message": "Invalid Authentication token!"}, 401
        except Exception as e:
            return {"message": f"Something went wrong: {str(e)}"}, 500
        return f(*args, **kwargs)
    return decorated