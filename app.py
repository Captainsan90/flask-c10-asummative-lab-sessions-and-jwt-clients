import os

from flask import Flask, jsonify

from config import Config
from extensions import bcrypt, cors, db, jwt, migrate
from routes.auth import auth_bp
from routes.notes import notes_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)

    @app.get("/")
    def index():
        return jsonify({"message": "Flask API is running"}), 200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5555))
    app.run(host="0.0.0.0", port=port, debug=True)