from flask import Flask, redirect, url_for, flash, render_template
from flask_login import login_required, logout_user
from .config import Config
from .models import db, login_manager, User
from .oauth import blueprint
from .cli import create_db


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(blueprint, url_prefix="/login")
app.cli.add_command(create_db)
db.init_app(app)
login_manager.init_app(app)

@login_manager.request_loader
def load_user(request):
    """Attempt to authenticate user using API key"""
    
    api_key = request.form.get('api_key')
    user = User.query.filter_by(api_key=api_key).first()
    if user:
        return user
    
    return None

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for("index"))


@app.route("/", methods=['POST','GET'])
def index():
    return render_template("home.html")
