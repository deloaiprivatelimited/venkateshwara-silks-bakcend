from flask import Flask
from mongoengine import connect
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    CORS(app)

    jwt = JWTManager(app)   # 🔑 THIS IS THE FIX
    # CORS(app)


    connect(
        host=os.getenv("MONGO_URI")
    )

    from routes.admin_user import admin_bp
    from routes.admin_auth import admin_auth_bp
    from routes.saree import saree_bp
    from routes.variety import variety_bp
    from routes.category import category_bp
    from routes.dashboard import dashboard_bp
    from routes.invite import invite_bp
    from routes.client  import client_bp
    app.register_blueprint(client_bp)
    app.register_blueprint(invite_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(variety_bp)
    app.register_blueprint(saree_bp)
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()

import os
if __name__ == "__main__":
    for rule in app.url_map.iter_rules():
        print(rule, rule.methods)
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )
