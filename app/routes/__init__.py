from .main import main
from .auth import auth
from .config import config

def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(config)