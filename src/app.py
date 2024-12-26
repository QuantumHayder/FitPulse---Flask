import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_htmx import HTMX
from src.blueprints.auth.routes import auth_bp, login_manager
from src.blueprints.base.routes import base_bp
from src.blueprints.client.routes import client_bp

from src.blueprints.admin.routes import admin_bp

from src.blueprints.trainer.routes import trainer_bp



app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(base_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(client_bp)
app.register_blueprint(trainer_bp)
login_manager.init_app(app)
htmx = HTMX(app)

if __name__ == "__main__":
    app.secret_key = os.getenv("SECRET_KEY")
    app.run("127.0.0.1", "8000", debug=True)
