from flask import Flask
from models import db
from routes import register_blueprints

app = Flask(__name__)

register_blueprints(app)

app.secret_key = 'sua_chave_secreta_aleatoria' 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

app.run(debug=True)