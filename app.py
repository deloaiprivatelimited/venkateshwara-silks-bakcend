from flask import Flask
from mongoengine import connect
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    connect(
        host=os.getenv("MONGO_URI")
    )

    from routes.admin_user import admin_bp
    app.register_blueprint(admin_bp)

    return app


app = create_app()
import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )

