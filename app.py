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
    jwt = JWTManager(app)   # 🔑 THIS IS THE FIX
    CORS(app)


    connect(
        host=os.getenv("MONGO_URI")
    )

    from routes.admin_user import admin_bp
    from routes.admin_auth import admin_auth_bp
    from routes.saree import saree_bp
    app.register_blueprint(saree_bp)
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )

