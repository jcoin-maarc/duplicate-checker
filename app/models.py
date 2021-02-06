from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_method
from config import Config
from cryptography.fernet import Fernet

db = SQLAlchemy()
config = Config()
fernet = Fernet(config.PARTICIPANT_INFO_KEY)

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    # Use for Oauth 2 authentication via Google
    email = db.Column(db.String(256), unique=True)
    # Generate with something like secrets.token_hex(32)
    api_key = db.Column(db.String(256))
    site_id = db.Column(db.Integer, db.ForeignKey(Site.id), nullable=False)
    site = db.relationship(Site)

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    info_encrypted = db.Column(db.LargeBinary, nullable=False)
    recruitment_date = db.Column(db.DateTime, server_default=func.now())
    recruited_by = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)
    
    def __init__(self, info=None, info_encrypted=None, **kwargs):
        if info_encrypted is None and info is not None:
            info_encrypted = fernet.encrypt(info.encode())
        super().__init__(info_encrypted=info_encrypted, **kwargs)
    
    @property
    def info(self):
        raise AttributeError('Participant.info is write-only')
    
    @info.setter
    def info(self, info):
        self.info_encrypted = fernet.encrypt(info.encode())
    
    @hybrid_method
    def match(self, info):
        return fernet.decrypt(self.info_encrypted) == info.encode()

# setup login manager
login_manager = LoginManager()
login_manager.login_view = 'google.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
