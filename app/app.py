from flask import Flask, render_template
from models import db
from routes import register_blueprints

app = Flask(__name__)

register_blueprints(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

app.run(debug=True)