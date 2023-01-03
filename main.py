import os
from flask import Flask
from flask_cors import CORS
from routes.user import users_bp
from routes.feed import feed_bp
from routes.rentals import rentals_bp
from routes.roommates import roommates_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(users_bp)
app.register_blueprint(feed_bp)
app.register_blueprint(rentals_bp)
app.register_blueprint(roommates_bp)

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))