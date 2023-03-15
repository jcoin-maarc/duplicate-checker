from flask import Flask, redirect, url_for, flash, render_template, request
from flask_login import login_required, logout_user, current_user
from config import Config
from .models import db, login_manager, User, Participant
from .oauth import blueprint
from .cli import create_db
from flask_bootstrap import Bootstrap4
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, RadioField, SubmitField, ValidationError
from wtforms.validators import InputRequired, length, Regexp
from cryptography.fernet import Fernet
from pytz import timezone
from flask import jsonify
from datetime import date

app = Flask(__name__)
app.config.from_object(Config)
# N.B. Uncomment to run behind reverse proxy, and start with
# SCRIPT_NAME=/<prefix> gunicorn --bind=192.168.0.112:9090 -w 4 'app:app'
# Also, make sure to preserve prefix through proxy.
# See https://dlukes.github.io/flask-wsgi-url-prefix.html for more info.
# app.wsgi_app = ProxyFix(
#     app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
# )
app.register_blueprint(blueprint, url_prefix='/login')
app.cli.add_command(create_db)
db.init_app(app)
login_manager.init_app(app)
bootstrap = Bootstrap4(app)
fernet = Fernet(app.config['PARTICIPANT_INFO_KEY'])

@login_manager.request_loader
def load_user(request):
    """Attempt to authenticate user using API key"""
    
    api_key = request.form.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    
    return None

@login_manager.unauthorized_handler
def unauthorized():
    """Respond to unauthorized requests"""
    
    if request.form.get('api_key'):
        return jsonify({"message":"Unauthorized request"}), 401
    
    return redirect(url_for('index'))

class ParticipantInfoForm(FlaskForm):
    first_initial = StringField('First initial', [InputRequired(),
                                length(max=1), Regexp('[a-zA-Z]')])
    last_initial = StringField('Last initial', [InputRequired(),
                               length(max=1), Regexp('[a-zA-Z]')])
    # N.B. Need to specify type="text" to suppress Safari's automatic datepicker
    dob = DateField('Date of birth', [InputRequired()], format='%m/%d/%Y',
                    render_kw={'type':'text', 'placeholder':'mm/dd/yyyy'})
    sex = RadioField('Assigned sex', [InputRequired()], choices=['Male','Female'])
    submit = SubmitField(label='Check for duplicates')
    
    def validate_dob(form, field):
        if field.data and (field.data > date.today()):
            raise ValidationError('Date of birth cannot be in the future')
        elif field.data and (field.data < date(1910, 1, 1)):
            raise ValidationError('Date of birth cannot be before 01/01/1910')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('home.html', form=ParticipantInfoForm())

def format_info(first_initial, last_initial, dob, sex):
    """Combine participant information into a single string in standardized format"""
    return '-'.join([first_initial+last_initial, dob.strftime('%Y-%m-%d'),
                     sex]).upper()

@app.route('/check', methods=['POST'])
@login_required
def check():
    
    api_key = request.form.get('api_key')
    form = (ParticipantInfoForm(meta={'csrf':False}) if api_key
            else ParticipantInfoForm())
    
    if form.validate_on_submit():
        info = format_info(form.first_initial.data, form.last_initial.data,
                           form.dob.data, form.sex.data)
        participants = Participant.query.all()
        dups = []
        for p in participants:
            if p.match(info):
                recruitment_date = p.recruitment_date.replace(tzinfo=timezone('UTC')).\
                                   astimezone(timezone('US/Central')).\
                                   strftime('%m/%d/%Y %I:%M %p %Z')
                dups.append({'site':p.user.site.name,
                          'recruited_by':p.user.username,
                          'recruitment_date':recruitment_date})
        
        if api_key:
            return jsonify({"duplicates":dups})
        
        else:
            form.submit.label.text = ('Add participant' if not dups
                                      else 'Override and add participant')
            return render_template('add.html', form=form, dups=dups)
    
    else:
        
        if api_key:
            return jsonify({"message":"Invalid request"}), 400
        else:
            return render_template('home.html', form=form)

@app.route('/add', methods=['POST'])
@login_required
def add():
    
    api_key = request.form.get('api_key')
    form = (ParticipantInfoForm(meta={'csrf':False}) if api_key
            else ParticipantInfoForm())
    
    if form.validate_on_submit():
        info = format_info(form.first_initial.data, form.last_initial.data,
                           form.dob.data, form.sex.data)
        participant = Participant(info=info, recruited_by=current_user.id)
        db.session.add(participant)
        db.session.commit()
        
        if api_key:
            return jsonify({"message":"Participant added"})
        else:
            flash('Participant added')
    
    if api_key:
        return jsonify({"message":"Invalid request"}), 400
    else:
        return redirect(url_for('index'))
